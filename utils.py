import cv2
import numpy as np
import logging

def process_image(image, pixels_per_cm=None):
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logging.error("No contours found")
            return None
        
        # Find the largest contour (assuming it's the shoe)
        shoe_contour = max(contours, key=cv2.contourArea)

        shoe_rect = cv2.minAreaRect(shoe_contour)
        box = cv2.boxPoints(shoe_rect)
        box = np.int32(box)  # Changed from np.int0 to np.int32

        # Get shoe dimensions in pixels
        (width, height) = shoe_rect[1]
        shoe_length = max(width, height)
        shoe_width = min(width, height)
        shoe_height = shoe_width * 0.3

        if pixels_per_cm is None or pixels_per_cm <= 0:
            logging.error("Invalid pixels_per_cm value")
            return None

        # Convert dimensions to cm using pixels_per_cm
        shoe_length /= pixels_per_cm
        shoe_width /= pixels_per_cm
        shoe_height /= pixels_per_cm

        volume = shoe_length * shoe_width * shoe_height

        cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

        if len(image.shape) == 2:  
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return {
            'length': round(shoe_length, 1),
            'width': round(shoe_width, 1),
            'height': round(shoe_height, 1),
            'volume': round(volume, 1),
            'processed_image': image
        }
    except Exception as e:
        logging.error(f"Error processing image: {e}", exc_info=True)
        return None

def calibrate(calibration_image, known_width_cm):
    try:
        result = process_image(calibration_image, pixels_per_cm=1) 
        if result is None:
            logging.error("Calibration failed: No object detected")
            return None

        detected_width_pixels = result['width']
        if detected_width_pixels <= 0:
            logging.error("Invalid detected width in pixels")
            return None

        pixels_per_cm = detected_width_pixels / known_width_cm
        logging.info(f"Calibration successful: {pixels_per_cm} pixels per cm")
        return pixels_per_cm
    except Exception as e:
        logging.error(f"Error during calibration: {e}", exc_info=True)
        return None
