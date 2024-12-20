import os
import boto3
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Load environment variables
load_dotenv()

class S3Handler:
    def __init__(self):
        # Initialize S3 client with OVH credentials
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv("OVH_ENDPOINT"),
            aws_access_key_id=os.getenv("OVH_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("OVH_SECRET_KEY"),
            region_name="us-east-1",
            config=boto3.session.Config(signature_version='s3v4')
        )
        self.bucket_name = os.getenv("OVH_BUCKET_NAME")
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}

    def upload_image(self, file):
        """Upload an image to the S3 bucket and return its URL."""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s3_key = f"{int.from_bytes(os.urandom(8), 'big')}-{filename}"

            try:
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={'ACL': 'public-read'}  # Make it publicly accessible
                )
                file_url = f"{os.getenv('OVH_ENDPOINT')}/{self.bucket_name}/{s3_key}"
                return {"success": True, "url": file_url}

            except NoCredentialsError:
                return {"success": False, "error": "No valid credentials found."}
            except PartialCredentialsError:
                return {"success": False, "error": "Incomplete credentials provided."}
            except Exception as e:
                return {"success": False, "error": f"Error uploading image: {str(e)}"}
        else:
            return {"success": False, "error": "Invalid file type."}

    def list_files(self):
        """List all files in the S3 bucket."""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                return {"success": True, "files": files}
            return {"success": True, "files": []}  # Empty bucket
        except Exception as e:
            return {"success": False, "error": f"Error listing files: {str(e)}"}

    def delete_file(self, file_key):
        """Delete a file from the S3 bucket."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return {"success": True, "message": f"File '{file_key}' deleted successfully."}
        except Exception as e:
            return {"success": False, "error": f"Error deleting file: {str(e)}"}

    def allowed_file(self, filename):
        """Check if the file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
