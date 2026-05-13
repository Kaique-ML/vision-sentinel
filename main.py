"""
VisionSentinel - Sistema de Detecção e Monitoramento por Visão Computacional
Ponto de entrada principal da aplicação.
"""

import cv2
import time
import argparse
import logging
from src.detector import Detector
from src.database import DatabaseManager
from src.utils import setup_logging, draw_detections

setup_logging()
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """
    Faz o parse dos argumentos de linha de comando.

    Returns:
        argparse.Namespace: Argumentos parseados com source, show e save_video.
    """
    parser = argparse.ArgumentParser(description="VisionSentinel - Motor de Detecção")
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Fonte de vídeo: '0' para webcam, caminho para arquivo ou URL de câmera IP",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Exibe o vídeo com bounding boxes em tempo real",
    )
    parser.add_argument(
        "--save-video",
        type=str,
        default=None,
        help="Caminho para salvar o vídeo processado (ex: output.mp4)",
    )
    return parser.parse_args()


def main():
    """
    Função principal. Orquestra captura, inferência, persistência e exibição.
    """
    args = parse_args()
    source = int(args.source) if args.source.isdigit() else args.source

    logger.info(f"Iniciando VisionSentinel | Fonte: {source}")

    detector = Detector()
    db = DatabaseManager()
    db.initialize()

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.error(f"Não foi possível abrir a fonte de vídeo: {source}")
        return

    writer = None
    if args.save_video:
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        writer = cv2.VideoWriter(
            args.save_video, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
        )
        logger.info(f"Gravando vídeo em: {args.save_video}")

    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Frame não recebido. Encerrando captura.")
                break

            frame_count += 1
            detections = detector.detect(frame)

            for det in detections:
                db.log_detection(
                    class_name=det["class_name"],
                    confidence=det["confidence"],
                    bbox=det["bbox"],
                )

            annotated = draw_detections(frame, detections)

            if writer:
                writer.write(annotated)

            if args.show:
                cv2.imshow("VisionSentinel", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Encerramento solicitado pelo usuário (tecla Q).")
                    break

    except KeyboardInterrupt:
        logger.info("Interrompido via teclado.")
    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        db.close()
        logger.info(f"Sessão encerrada. Frames processados: {frame_count}")


if __name__ == "__main__":
    main()
