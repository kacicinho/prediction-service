from flask import Flask, request, jsonify
from s3_handler import S3Handler  # Import the S3Handler class
from kafka_handler import KafkaHandler  # Import the KafkaHandler class
from image_service import save_image, process_image  # Import functions from image_service.py
from db import init_db  # Import database initialization function

app = Flask(__name__)

# Initialize handlers
s3_handler = S3Handler()
kafka_handler = KafkaHandler()

# Initialize the database during app startup
@app.before_first_request
def setup_database():
    init_db()  # Call init_db once to initialize everything

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Endpoint to upload image and process it.
    """
    file = request.files.get('file')  # Get the image file from the request
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    # Save image to S3
    image_url = s3_handler.save_image(file)

    # Send the image event to Kafka for processing
    kafka_handler.send_event(image_url)

    return jsonify({'message': 'Image uploaded and processing started'}), 200

@app.route('/result', methods=['POST'])
def get_result():
    """
    Endpoint to get the result of the image processing.
    """
    image_url = request.json.get('image_url')
    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400

    result = get_result(image_url)

    return jsonify({'result': result}), 200

if __name__ == '__main__':
    app.run(debug=True)
