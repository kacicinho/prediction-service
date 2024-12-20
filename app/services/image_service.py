import os
import boto3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Load environment variables
load_dotenv()

# Get OVH credentials from .env file
OVH_ENDPOINT = os.getenv("OVH_ENDPOINT")
OVH_ACCESS_KEY = os.getenv("OVH_ACCESS_KEY")
OVH_SECRET_KEY = os.getenv("OVH_SECRET_KEY")
OVH_BUCKET_NAME = os.getenv("OVH_BUCKET_NAME")

s3_client = boto3.client(
    's3',
    endpoint_url=OVH_ENDPOINT,
    aws_access_key_id=OVH_ACCESS_KEY,
    aws_secret_access_key=OVH_SECRET_KEY,
    region_name="us-east-1",
    config=boto3.session.Config(signature_version='s3v4')
)

def get_result():
    """
    Endpoint to retrieve image details from the PostgreSQL database.
    Input: JSON body with `image_id`
    Output: JSON with image details or error message.
    """
    request_data = request.get_json()
    if not request_data or 'image_id' not in request_data:
        return jsonify({"success": False, "error": "Missing 'image_id' in request body."}), 400

    image_id = request_data['image_id']

    try:
        image_data = get_image_by_id(image_id)

        if image_data:
            return jsonify({"success": True, "data": image_data}), 200
        else:
            return jsonify({"success": False, "error": "Image not found."}), 404

    except Exception as e:
        return jsonify({"success": False, "error": f"Error fetching image: {str(e)}"}), 500

def upload_image():
    """
    Endpoint to upload an image to the S3 bucket and send an event to Kafka.
    Returns 200 OK with the file URL if successful.
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected for upload."}), 400

    # Upload the file to S3
    result = s3_handler.upload_image(file)
    if result['success']:
        # File uploaded successfully, send event to Kafka
        event_data = {
            "event": "file_uploaded",
            "file_url": result['url'],
            "filename": file.filename
        }
        kafka_response = kafka_handler.send_event(event_data)
        if kafka_response['success']:
            return jsonify({"success": True, "url": result['url']}), 200
        else:
            return jsonify({"success": False, "error": kafka_response['error']}), 500
    else:
        return jsonify({"success": False, "error": result['error']}), 500