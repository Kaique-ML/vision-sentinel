"""
Utilitários compartilhados: logging, desenho de anotações e helpers gerais.
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Any

# Paleta de cores por classe (BGR)
CLASS_COLORS: Dict[str, tuple] = {
    "person":   (0, 200, 255),
    "car":      (50, 205, 50),
    "truck":    (255, 140, 0),
    "bicycle":  (138, 43, 226),
    "default":  (180, 180, 180),
}


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configura o sistema de logging com formato padronizado.

    Args:
        level (int): Nível de log (ex: logging.INFO, logging.DEBUG).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def draw_detections(frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """
    Desenha os bounding boxes e labels sobre o frame original.

    Args:
        frame (np.ndarray): Frame original em BGR.
        detections (list): Lista de detecções retornada pelo Detector.

    Returns:
        np.ndarray: Frame anotado com bounding boxes e labels.
    """
    annotated = frame.copy()

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = f"{det['class_name']} {det['confidence']:.0%}"
        color = CLASS_COLORS.get(det["class_name"], CLASS_COLORS["default"])

        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(
            annotated,
            label,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    # HUD — contador no canto superior esquerdo
    count_text = f"Deteccoes: {len(detections)}"
    cv2.putText(
        annotated,
        count_text,
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return annotated
