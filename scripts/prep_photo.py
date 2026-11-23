"""One-time, local: cut the portrait out of its flat background and lift its
local contrast, so the ASCII pass sees the subject and nothing else.

    python scripts/prep_photo.py source-photo.jpg   ->  source-prepped.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def main(src):
    img = cv2.imread(str(src))
    h, w = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)

    # The backdrop is one flat colour: take it from the border, mark every
    # pixel close to it, and keep only the part of that mask touching the edge.
    border = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    bg = np.median(border, axis=0)
    near = (np.linalg.norm(lab - bg, axis=2) < 14).astype(np.uint8)
    n, labels = cv2.connectedComponents(near)
    edge_ids = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]])))
    edge_ids.discard(0)
    background = np.isin(labels, list(edge_ids))
    background = cv2.morphologyEx(background.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray[background] = 0  # black: the empty end of the ramp on a dark terminal

    out = ROOT / "source-prepped.png"
    cv2.imwrite(str(out), gray)
    print(f"wrote {out.name}  ({w}x{h}, {background.mean():.0%} background)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "source-photo.jpg")
