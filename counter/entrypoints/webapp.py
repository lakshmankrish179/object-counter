from io import BytesIO
from logger_config import logger  
from flask import Flask, request, jsonify
from counter import config


# Initialize logger for this module
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    count_action = config.get_count_action()  # Initialize count action logic

    # Endpoint to perform object counting
    @app.route('/api/object-count', methods=['POST'])
    def object_detection():
        logger.info("Received object-count request.")  # Log endpoint entry
        try:
            # Extract threshold and model name from request form data
            threshold = float(request.form.get('threshold', 0.5))
            model_name = request.form.get('model_name', "rfcn")
            uploaded_file = request.files.get('file')

            # Validate uploaded file presence
            if uploaded_file is None:
                logger.warning("No file provided in object-count request.")
                return jsonify({"error": "File is required"}), 400

            logger.debug(f"Threshold received: {threshold}, Model: {model_name}")

            # Read and save uploaded image to memory
            image = BytesIO()
            uploaded_file.save(image)
            image.seek(0)  # Reset the stream position

            # Execute object counting action
            count_response = count_action.execute(image, threshold)

            logger.info("Object counting executed successfully.")
            logger.debug(f"Count Response: {count_response}")

            # Return counting response as JSON
            return jsonify(count_response)

        except Exception as e:
            logger.exception(f"Error during object-count: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # Endpoint to perform object predictions
    @app.route('/api/predict-object', methods=['POST'])
    def predict_object():
        logger.info("Received predict-object request.")  # Log endpoint entry
        try:
            # Extract threshold and model name from request form data
            threshold = float(request.form.get('threshold', 0.5))
            model_name = request.form.get('model_name', "rfcn")
            uploaded_file = request.files.get('file')

            # Validate uploaded file presence
            if uploaded_file is None:
                logger.warning("No file provided in predict-object request.")
                return jsonify({"error": "File is required"}), 400

            logger.debug(f"Threshold received: {threshold}, Model: {model_name}")

            # Read and save uploaded image to memory
            image = BytesIO()
            uploaded_file.save(image)
            image.seek(0)  # Reset the stream position

            # Execute object prediction action
            prediction_response = count_action.predict(image, threshold)

            logger.info("Object prediction executed successfully.")
            logger.debug(f"Prediction Response: {prediction_response}")

            # Return prediction response as JSON
            return jsonify(prediction_response)

        except Exception as e:
            logger.exception(f"Error during predict-object: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return app

# Run Flask app in debug mode on host '0.0.0.0' if executed as main script
if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Flask application on 0.0.0.0:5000")
    app.run('0.0.0.0', debug=True)
