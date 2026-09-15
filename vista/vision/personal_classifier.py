"""Runtime adapter for the personally trained face classifier."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision.models import resnet50
from torchvision import transforms


MODEL_PATH = Path(
    os.getenv(
        "VISTA_FACE_MODEL",
        Path(__file__).resolve().parents[2] / "training_results" / "best_model_npz_splitB.pth",
    )
)
MODEL_THRESHOLD = float(os.getenv("VISTA_FACE_MODEL_THRESHOLD", "0.60"))
DEVICE = torch.device("cuda" if os.getenv("VISTA_FACE_MODEL_DEVICE") == "cuda" and torch.cuda.is_available() else "cpu")


class ResNet50FaceClassifier(nn.Module):
    """Architecture used by train_from_npz.py for the personal checkpoint."""

    def __init__(self, num_classes: int):
        super().__init__()
        backbone = resnet50(weights=None)
        self.features = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu,
            backbone.maxpool,
            backbone.layer1,
            backbone.layer2,
            backbone.layer3,
            backbone.layer4,
            backbone.avgpool,
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.BatchNorm1d(2048),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(images))


@lru_cache(maxsize=1)
def _load_model() -> tuple[nn.Module, list[str], Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Personal face model not found: {MODEL_PATH}. "
            "Download the Git LFS artifact or set VISTA_FACE_MODEL."
        )

    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    class_names = [str(name) for name in checkpoint["class_names"]]
    model = ResNet50FaceClassifier(len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    preprocessing = transforms.Compose([
        transforms.Resize((112, 112)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ])
    return model, class_names, preprocessing


def classify_face(face_rgb: np.ndarray) -> dict[str, Any]:
    """Classify one RGB face crop with the personal trained checkpoint."""
    if face_rgb.size == 0:
        return {"student_id": None, "confidence": 0.0}

    model, class_names, preprocessing = _load_model()
    image = Image.fromarray(face_rgb.astype(np.uint8), mode="RGB")
    tensor = preprocessing(image).unsqueeze(0).to(DEVICE)

    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
        confidence, class_index = torch.max(probabilities, dim=0)

    score = float(confidence.item())
    student_id = class_names[int(class_index.item())] if score >= MODEL_THRESHOLD else None
    return {"student_id": student_id, "confidence": score}


def model_info() -> dict[str, Any]:
    """Return loaded model metadata for health checks and diagnostics."""
    _, class_names, _ = _load_model()
    return {
        "model": "personal_resnet50",
        "checkpoint": str(MODEL_PATH),
        "device": str(DEVICE),
        "threshold": MODEL_THRESHOLD,
        "classes": len(class_names),
        "class_names": class_names,
    }