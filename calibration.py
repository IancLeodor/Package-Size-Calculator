import requests
import base64
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def perform_calibration(image_path, known_width_cm, server_url):
    try:
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        data = {
            'image': f'data:image/jpeg;base64,{image_data}',
            'known_width_cm': known_width_cm
        }

        response = requests.post(f'{server_url}/calibrate', json=data, verify=False)

        if response.status_code == 200:
            calibration_data = response.json()
            logger.info("Calibration successful: %s", calibration_data)
            return calibration_data
        else:
            logger.error("Calibration failed: %s", response.json())
            return None
    except Exception as e:
        logger.exception("An error occurred during calibration: %s", e)
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Perform calibration")
    parser.add_argument('--image_path', type=str, required=True, help="Path to the calibration image")
    parser.add_argument('--known_width_cm', type=float, required=True, help="Known width of the object in cm")
    parser.add_argument('--server_url', type=str, required=True, help="URL of the server for calibration")
    args = parser.parse_args()

    result = perform_calibration(args.image_path, args.known_width_cm, args.server_url)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
