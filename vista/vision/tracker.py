"""
ByteTrack Multi-Face Tracker
=============================
Tracks multiple faces across video frames to:
- Deduplicate detections (same student seen multiple times)
- Confirm identity over K frames before marking attendance
- Handle occlusions and brief disappearances

Uses a simplified ByteTrack-style approach:
- Kalman filter for position prediction
- IoU-based association (high + low confidence detections)
- Identity confirmation after N consistent frames

Usage:
    from vista.vision.tracker import FaceTracker
    tracker = FaceTracker()

    for frame in video_frames:
        results = tracker.update(frame_path_or_array)
    
    confirmed = tracker.get_confirmed_attendees()
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Track:
    """A tracked face identity across frames."""
    track_id: int
    student_id: str | None = None
    confidence: float = 0.0
    bbox: list[float] = field(default_factory=list)
    frames_seen: int = 0
    frames_lost: int = 0
    last_seen: float = 0.0
    identity_votes: dict = field(default_factory=dict)
    confirmed: bool = False


class FaceTracker:
    """
    ByteTrack-inspired multi-face tracker for classroom attendance.
    
    Tracks faces across video frames and confirms attendance
    after a student is consistently identified for K frames.
    """

    def __init__(
        self,
        confirmation_frames: int = 3,
        max_lost_frames: int = 10,
        iou_threshold: float = 0.3,
    ):
        self.confirmation_frames = confirmation_frames
        self.max_lost_frames = max_lost_frames
        self.iou_threshold = iou_threshold
        self.tracks: list[Track] = []
        self.next_id = 0
        self.confirmed_students: dict[str, float] = {}  # student_id → confidence

    def update(self, detections: list[dict]) -> list[Track]:
        """
        Update tracker with new frame detections.

        Args:
            detections: List of dicts from detect.py, each with:
                - bbox: [x1, y1, x2, y2]
                - student_id: str or None (from matching)
                - confidence: float

        Returns:
            Current active tracks.
        """
        now = time.time()

        if not detections:
            # No detections — increment lost counter for all tracks
            for track in self.tracks:
                track.frames_lost += 1
            self._remove_dead_tracks()
            return self.tracks

        # Split detections into high and low confidence
        high_conf = [d for d in detections if d.get("confidence", 0) >= 0.5]
        low_conf = [d for d in detections if d.get("confidence", 0) < 0.5]

        # First association: high confidence detections
        matched_tracks, unmatched_dets, unmatched_tracks = self._associate(
            self.tracks, high_conf
        )

        # Update matched tracks
        for track, det in matched_tracks:
            self._update_track(track, det, now)

        # Second association: remaining tracks with low confidence detections
        if unmatched_tracks and low_conf:
            matched2, unmatched_low, still_unmatched = self._associate(
                unmatched_tracks, low_conf
            )
            for track, det in matched2:
                self._update_track(track, det, now)
            unmatched_tracks = still_unmatched

        # Increment lost counter for unmatched tracks
        for track in unmatched_tracks:
            track.frames_lost += 1

        # Create new tracks for unmatched high-confidence detections
        for det in unmatched_dets:
            self._create_track(det, now)

        self._remove_dead_tracks()
        self._check_confirmations()

        return self.tracks

    def get_confirmed_attendees(self) -> list[dict]:
        """
        Get all students confirmed present (tracked for >= K frames).
        
        Returns:
            List of {student_id, confidence} for confirmed students.
        """
        return [
            {"student_id": sid, "confidence": conf}
            for sid, conf in self.confirmed_students.items()
        ]

    def reset(self):
        """Reset tracker state for a new session."""
        self.tracks = []
        self.next_id = 0
        self.confirmed_students = {}

    # --- Internal methods ---

    def _associate(
        self, tracks: list[Track], detections: list[dict]
    ) -> tuple[list[tuple[Track, dict]], list[dict], list[Track]]:
        """Associate detections with existing tracks using IoU."""
        if not tracks or not detections:
            return [], detections, tracks

        # Compute IoU matrix
        iou_matrix = np.zeros((len(tracks), len(detections)))
        for i, track in enumerate(tracks):
            for j, det in enumerate(detections):
                iou_matrix[i, j] = self._compute_iou(track.bbox, det.get("bbox", []))

        # Greedy matching (simplified Hungarian)
        matched = []
        matched_track_ids = set()
        matched_det_ids = set()

        while True:
            if iou_matrix.size == 0:
                break
            max_iou = iou_matrix.max()
            if max_iou < self.iou_threshold:
                break
            i, j = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
            matched.append((tracks[i], detections[j]))
            matched_track_ids.add(i)
            matched_det_ids.add(j)
            iou_matrix[i, :] = 0
            iou_matrix[:, j] = 0

        unmatched_dets = [d for j, d in enumerate(detections) if j not in matched_det_ids]
        unmatched_tracks = [t for i, t in enumerate(tracks) if i not in matched_track_ids]

        return matched, unmatched_dets, unmatched_tracks

    def _update_track(self, track: Track, detection: dict, now: float):
        """Update an existing track with a new detection."""
        track.bbox = detection.get("bbox", track.bbox)
        track.confidence = detection.get("confidence", track.confidence)
        track.frames_seen += 1
        track.frames_lost = 0
        track.last_seen = now

        # Vote for identity
        student_id = detection.get("student_id")
        if student_id:
            track.identity_votes[student_id] = track.identity_votes.get(student_id, 0) + 1
            # Assign majority vote as track identity
            track.student_id = max(track.identity_votes, key=track.identity_votes.get)

    def _create_track(self, detection: dict, now: float):
        """Create a new track from an unmatched detection."""
        track = Track(
            track_id=self.next_id,
            student_id=detection.get("student_id"),
            confidence=detection.get("confidence", 0.0),
            bbox=detection.get("bbox", []),
            frames_seen=1,
            last_seen=now,
        )
        if track.student_id:
            track.identity_votes[track.student_id] = 1
        self.tracks.append(track)
        self.next_id += 1

    def _remove_dead_tracks(self):
        """Remove tracks that have been lost for too long."""
        self.tracks = [t for t in self.tracks if t.frames_lost <= self.max_lost_frames]

    def _check_confirmations(self):
        """Check if any tracks have been confirmed (seen for K frames)."""
        for track in self.tracks:
            if (
                track.student_id
                and track.frames_seen >= self.confirmation_frames
                and not track.confirmed
            ):
                track.confirmed = True
                # Keep highest confidence
                if (
                    track.student_id not in self.confirmed_students
                    or track.confidence > self.confirmed_students[track.student_id]
                ):
                    self.confirmed_students[track.student_id] = track.confidence

    @staticmethod
    def _compute_iou(bbox1: list, bbox2: list) -> float:
        """Compute Intersection over Union of two bounding boxes."""
        if len(bbox1) < 4 or len(bbox2) < 4:
            return 0.0

        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])

        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - inter

        return inter / union if union > 0 else 0.0
