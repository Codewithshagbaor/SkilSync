import requests
from django.conf import settings
from rest_framework.response import Response

PINATA_API_KEY = settings.PINATA_API_KEY
PINATA_SECRET_API_KEY = settings.PINATA_SECRET_API_KEY
PINATA_API_URL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'
import logging
import traceback

logger = logging.getLogger(__name__)
def upload_to_pinata(file):
    try:
        # Log detailed file information
        logger.info(f"Attempting to upload file: {file.name}")
        logger.info(f"File size: {file.size} bytes")
        logger.info(f"File content type: {file.content_type}")

        # Verify API keys are present
        if not PINATA_API_KEY or not PINATA_SECRET_API_KEY:
            logger.error("Pinata API keys are missing")
            raise ValueError("Pinata API keys are not configured")

        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        
        # Log headers (without exposing secret key)
        logger.info(f"Pinata API URL: {url}")
        logger.info(f"Using API Key: {PINATA_API_KEY[:5]}...")

        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_API_KEY
        }
        
        files = {"file": (file.name, file, file.content_type)}
        
        # Log before making the request
        logger.info("Sending file to Pinata...")

        response = requests.post(url, headers=headers, files=files)
        
        # Log full response details
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")

        # Raise an exception for bad responses
        response.raise_for_status()

        # Extract and log IPFS hash
        response_json = response.json()
        ipfs_hash = response_json.get("IpfsHash")
        
        if not ipfs_hash:
            logger.error("No IPFS hash found in Pinata response")
            raise ValueError("Failed to get IPFS hash from Pinata")

        pinata_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        logger.info(f"File successfully uploaded. IPFS URL: {pinata_url}")

        return pinata_url

    except requests.exceptions.RequestException as e:
        # Detailed logging for request-related exceptions
        logger.error(f"Pinata upload request failed: {str(e)}")
        logger.error(f"Request exception details: {traceback.format_exc()}")
        raise Exception(f"Failed to upload file to Pinata: {str(e)}")
    
    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.error(f"Unexpected error in Pinata upload: {str(e)}")
        logger.error(f"Full error traceback: {traceback.format_exc()}")
        raise Exception(f"Unexpected error uploading to Pinata: {str(e)}")
