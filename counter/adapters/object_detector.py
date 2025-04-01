import json
from typing import List, BinaryIO
from logger_config import logger 

import numpy as np
import requests
from PIL import Image

from counter.domain.models import Prediction, Box
from counter.domain.ports import ObjectDetector



class FakeObjectDetector(ObjectDetector):
    def predict(self, image: BinaryIO) -> List[Prediction]:
        logger.info("FakeObjectDetector: Generating fake predictions.")
        predictions = [
            Prediction(
                class_name='cat',
                score=0.999190748,
                box=Box(
                    xmin=0.367288858,
                    ymin=0.278333426,
                    xmax=0.735821366,
                    ymax=0.6988855
                )
            )
        ]
        logger.debug(f"Fake predictions generated: {predictions}")
        return predictions


class TFSObjectDetector(ObjectDetector):
    def __init__(self, host: str, port: int, model: str):
        self.url = f"http://{host}:{port}/v1/models/{model}:predict"
        logger.info(f"Initializing TFSObjectDetector with URL: {self.url}")
        self.classes_dict = self._build_classes_dict()

    def predict(self, image: BinaryIO) -> List[Prediction]:
        np_image = self._to_np_array(image)
        predict_request = json.dumps({"instances": np.expand_dims(np_image, 0).tolist()})
        
        logger.info(f"Sending prediction request to TensorFlow Serving at: {self.url}")
        response = requests.post(self.url, data=predict_request)
        
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}: {response.text}")
            response.raise_for_status()

        predictions = response.json()['predictions'][0]
        logger.info("Successfully received predictions from TensorFlow Serving.")

        return self._raw_predictions_to_domain(predictions)

    @staticmethod
    def _build_classes_dict():
        labels_path = 'counter/adapters/mscoco_label_map.json'
        logger.info(f"Loading class labels from: {labels_path}")
        with open(labels_path) as json_file:
            labels = json.load(json_file)
            classes_dict = {label['id']: label['display_name'] for label in labels}
        logger.debug(f"Class labels loaded: {classes_dict}")
        return classes_dict

    @staticmethod
    def _to_np_array(image: BinaryIO) -> np.ndarray:
        logger.info("Converting input image to NumPy array.")
        image_pil = Image.open(image)
        np_array = np.array(image_pil)
        logger.debug(f"Converted image shape: {np_array.shape}")
        return np_array

    def _raw_predictions_to_domain(self, raw_predictions: dict) -> List[Prediction]:
        logger.info("Parsing raw predictions into domain objects.")
        num_detections = int(raw_predictions.get('num_detections', 0))
        predictions = []

        for i in range(num_detections):
            detection_box = raw_predictions['detection_boxes'][i]
            box = Box(
                xmin=detection_box[1],
                ymin=detection_box[0],
                xmax=detection_box[3],
                ymax=detection_box[2]
            )
            detection_score = raw_predictions['detection_scores'][i]
            detection_class = raw_predictions['detection_classes'][i]
            class_name = self.classes_dict.get(detection_class, "Unknown")

            prediction = Prediction(
                class_name=class_name,
                score=detection_score,
                box=box
            )
            predictions.append(prediction)

        logger.debug(f"Parsed predictions: {predictions}")
        return predictions
