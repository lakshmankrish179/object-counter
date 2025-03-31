from logger_config import logger  
from typing import Dict, Any, List
from counter.domain.ports import ObjectDetector, ObjectCountRepo


class CountObjectsAction:
    """
    Action class for counting objects detected in an image based on a given threshold.
    """
    
    def __init__(self, detector: ObjectDetector, repo: ObjectCountRepo):
        self.detector = detector
        self.repo = repo

    def execute(self, image: Any, threshold: float) -> Dict[str, Any]:
        """
        Detects and counts objects in the provided image above the confidence threshold.
        
        :param image: The image file or stream to process.
        :param threshold: Confidence threshold for filtering detected objects.
        :return: A dictionary with counted objects and total.
        """
        try:
            logger.info("Starting object detection action.")

            # Perform object detection
            detections = self.detector.detect(image)
            logger.debug(f"Raw detections received: {detections}")

            # Filter detections based on threshold
            filtered_detections = [
                det for det in detections if det.confidence >= threshold
            ]
            logger.debug(f"Filtered detections: {filtered_detections}")

            # Count detected objects grouped by class
            counts = self._count_objects(filtered_detections)
            logger.info(f"Object counts computed: {counts}")

            # Save counts to the repository
            self.repo.save_counts(counts, threshold)
            logger.info("Counts successfully saved to repository.")

            # Return response
            return {
                "counts": counts,
                "total": sum(counts.values())
            }

        except Exception as e:
            logger.exception(f"Error during object counting action: {e}")
            raise

    def _count_objects(self, detections: List[Any]) -> Dict[str, int]:
        """
        Helper method to count occurrences of each detected object class.
        
        :param detections: List of detections after applying threshold.
        :return: Dictionary with object class as key and count as value.
        """
        counts = {}
        for detection in detections:
            class_name = detection.object_class
            counts[class_name] = counts.get(class_name, 0) + 1
            logger.debug(f"Counting object: {class_name}, current count: {counts[class_name]}")
        return counts
