# Built-in imports
import os
import json
from dataclasses import dataclass, field

# Third party imports
import supervision as sv
from ultralytics import YOLO

# Local imports
from yonata.benchmark import benchmark_from_image_folder


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
        return_value = {"detections": results}
        return return_value

    def process(self, image, raw_result: bool = False):
        image = self.preprocess(image)

        results = self._model.predict(source=image, save=False, verbose=True, device=0)
        results = results[0]

        if raw_result:
            return results

        results = self.postprocess(results)
        return results


def main():
    detector = ObjectDetection()
    folder_path = "/home/user/yonata/local/image"

    benchmark_from_image_folder(instance=detector, folder_path=folder_path)


if __name__ == "__main__":
    main()
