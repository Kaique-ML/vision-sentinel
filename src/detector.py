"""
Módulo de inferência com YOLOv8.
Responsável por carregar o modelo e executar detecções nos frames.
"""

import logging
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()
logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "models/yolov8n.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.45"))
TARGET_CLASSES = os.getenv("TARGET_CLASSES", "person,car,truck,bicycle").split(",")


class Detector:
    """
    Wrapper do YOLOv8 para detecção de objetos em frames de vídeo.

    Attributes:
        model: Instância do modelo YOLO carregado.
        confidence: Limiar mínimo de confiança para aceitar uma detecção.
        target_classes: Lista de classes que devem ser detectadas e registradas.
    """

    def __init__(self):
        logger.info(f"Carregando modelo YOLO de: {MODEL_PATH}")
        self.model = YOLO(MODEL_PATH)
        self.confidence = CONFIDENCE_THRESHOLD
        self.target_classes = [c.strip().lower() for c in TARGET_CLASSES]
        logger.info(
            f"Modelo carregado | Confiança mínima: {self.confidence} | "
            f"Classes alvo: {self.target_classes}"
        )

    def detect(self, frame) -> List[Dict[str, Any]]:
        """
        Executa inferência em um único frame e retorna as detecções filtradas.

        Args:
            frame: Frame de imagem em formato numpy array (BGR, OpenCV).

        Returns:
            Lista de dicionários, cada um contendo:
                - class_name (str): Nome da classe detectada.
                - confidence (float): Confiança da detecção (0.0 a 1.0).
                - bbox (tuple): Coordenadas do bounding box (x1, y1, x2, y2).
        """
        results = self.model(frame, verbose=False)[0]
        detections = []

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.confidence:
                continue

            class_id = int(box.cls[0])
            class_name = self.model.names[class_id].lower()

            if self.target_classes and class_name not in self.target_classes:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append(
                {
                    "class_name": class_name,
                    "confidence": round(conf, 4),
                    "bbox": (x1, y1, x2, y2),
                }
            )

        return detections
