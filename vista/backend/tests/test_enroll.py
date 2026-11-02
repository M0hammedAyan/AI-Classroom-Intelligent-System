"""Regression tests for face enrollment validation and failure handling."""

import base64
import subprocess
import sys
from pathlib import Path


def test_backend_launch_exposes_vision_package():
    backend_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import app.main; import vista.vision.enroll",
        ],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_enroll_rejects_unsupported_format(client, admin_headers):
    response = client.post(
        "/api/v1/students/CS22B001/enroll",
        headers=admin_headers,
        json={"images": [base64.b64encode(b"not an image").decode()]},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "UNSUPPORTED_FORMAT"


def test_enroll_returns_no_face_error(client, admin_headers, monkeypatch):
    from vista.vision import enroll as vision_enroll

    monkeypatch.setattr(
        vision_enroll,
        "enroll_student",
        lambda student_id, image_paths: {
            "enrolled": False,
            "images_processed": 0,
            "images_failed": 1,
            "embedding_quality": "poor",
            "error": "No faces detected in any provided images",
        },
    )

    # Minimal valid PNG; the vision call is mocked for this input contract test.
    import cv2
    import numpy as np
    _, encoded = cv2.imencode(".png", np.zeros((1, 1, 3), dtype=np.uint8))
    png = base64.b64encode(encoded.tobytes()).decode()
    response = client.post(
        "/api/v1/students/CS22B001/enroll",
        headers=admin_headers,
        json={"images": [png]},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "NO_FACE_DETECTED"
    assert "No faces detected" in response.json()["detail"]["message"]
