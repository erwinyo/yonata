# Built-in imports
import os
import json
from dataclasses import dataclass, field

# Third party imports
import supervision as sv
from ultralytics import YOLO

# Local imports


@dataclass(frozen=False, kw_only=False, match_args=False, slots=False)
class ObjectDetection:
    config: dict = field(default_factory=dict)

    _model: YOLO = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._model = YOLO(model="yolov10n.pt", task="detect")

    def preprocess(self, image):
        return image

    def postprocess(self, results):
        sv_detections = sv.Detections.from_ultralytics(results)

        results = []
        confidences = sv_detections.confidence
        class_ids = sv_detections.class_id
        for confidence, class_id in zip(confidences, class_ids):
            label = self._model.names[class_id]
            results.append(
                {
                    "label": label,
                    "confidence": float(confidence),
                    "class_id": int(class_id),
                }
            )
        return results

    def process(self, image, raw_result: bool = False):
        image = self.preprocess(image)

        results = self._model.predict(source=image, save=False, verbose=True, device=0)
        results = results[0]

        if raw_result:
            return results

        results = self.postprocess(results)
        return results


from yonata import Yonata
from yonata.core import PostgresConnection, MinioConnection


def main():
    detector = ObjectDetection()
    folder_path = "/home/user/yonata/local/image"

    postgres_connection = PostgresConnection(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="127.0.0.1",
        port="5432",
    )
    minio_connection = MinioConnection(
        host="127.0.0.1",
        port="9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False,
    )

    audit = Yonata(
        postgres_connection=postgres_connection,
        minio_connection=minio_connection,
    )
    print("Audit instance created successfully")
    # audit.do_benchmark_from_image_folder(instance=detector, folder_path=folder_path)

    # benchmark_from_image_folder(instance=detector, folder_path=folder_path)


if __name__ in {"__main__", "__mp_main__"}:
    main()
    # test_nicegui()
