# # import ssl
# # from flask import Flask, request, render_template, jsonify, send_file
# # from flask_migrate import Migrate
# # from flask_sqlalchemy import SQLAlchemy
# # import base64
# # import cv2
# # import numpy as np
# # import logging
# # from sqlalchemy.dialects.mysql import LONGTEXT
# # from calibration import perform_calibration  # Import the calibration function
# # import time
# # import requests

# # app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:aaaaaaaaaa@localhost/cube_calculator'
# # db = SQLAlchemy(app)
# # migrate = Migrate(app, db)

# # logging.basicConfig(level=logging.DEBUG)
# # logger = logging.getLogger(__name__)

# # class Result(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     length = db.Column(db.Integer, nullable=False)
# #     width = db.Column(db.Integer, nullable=False)
# #     height = db.Column(db.Integer, nullable=False)
# #     volume = db.Column(db.Integer, nullable=False)
# #     processed_image = db.Column(LONGTEXT, nullable=True)
# #     created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# # def create_tables():
# #     with app.app_context():
# #         db.create_all()

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # def process_image(image, pixels_per_cm=None):
# #     try:
# #         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# #         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
# #         # Edge detection
# #         edges = cv2.Canny(blurred, 50, 150)
        
# #         # Find contours
# #         contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
# #         if not contours:
# #             logging.error("No contours found")
# #             return None
        
# #         # Find the largest contour (assuming it's the shoe)
# #         shoe_contour = max(contours, key=cv2.contourArea)

# #         # Get bounding rectangle
# #         shoe_rect = cv2.minAreaRect(shoe_contour)
# #         box = cv2.boxPoints(shoe_rect)
# #         box = np.int32(box)  # Changed from np.int0 to np.int32

# #         # Get shoe dimensions in pixels
# #         (width, height) = shoe_rect[1]
# #         shoe_length = max(width, height)
# #         shoe_width = min(width, height)
# #         shoe_height = shoe_width * 0.3  # Estimate height as 30% of width

# #         if pixels_per_cm is None or pixels_per_cm <= 0:
# #             logging.error("Invalid pixels_per_cm value")
# #             return None

# #         # Convert dimensions to cm using pixels_per_cm
# #         shoe_length /= pixels_per_cm
# #         shoe_width /= pixels_per_cm
# #         shoe_height /= pixels_per_cm

# #         # Calculate volume (in cm³)
# #         volume = shoe_length * shoe_width * shoe_height

# #         # Draw contour on the original image
# #         cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

# #         # Ensure the image is in BGR format
# #         if len(image.shape) == 2:  # If grayscale, convert to BGR
# #             image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# #         return {
# #             'length': round(shoe_length, 1),
# #             'width': round(shoe_width, 1),
# #             'height': round(shoe_height, 1),
# #             'volume': round(volume, 1),
# #             'processed_image': image
# #         }
# #     except Exception as e:
# #         logging.error(f"Error processing image: {e}", exc_info=True)
# #         return None

# # def calibrate(calibration_image, known_width_cm):
# #     try:
# #         result = process_image(calibration_image, pixels_per_cm=1)  # Temporarily set to 1 for raw pixel value
# #         if result is None:
# #             logging.error("Calibration failed: No object detected")
# #             return None

# #         detected_width_pixels = result['width']
# #         if detected_width_pixels <= 0:
# #             logging.error("Invalid detected width in pixels")
# #             return None

# #         pixels_per_cm = detected_width_pixels / known_width_cm
# #         logging.info(f"Calibration successful: {pixels_per_cm} pixels per cm")
# #         return pixels_per_cm
# #     except Exception as e:
# #         logging.error(f"Error during calibration: {e}", exc_info=True)
# #         return None

# # @app.route('/calibrate', methods=['POST'])
# # def calibrate_route():
# #     try:
# #         data = request.get_json()
# #         image_data = base64.b64decode(data['image'].split(',')[1])
# #         known_width_cm = float(data['known_width_cm'])
# #         np_arr = np.frombuffer(image_data, np.uint8)
# #         image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

# #         global PIXELS_PER_CM
# #         PIXELS_PER_CM = calibrate(image, known_width_cm)
        
# #         if PIXELS_PER_CM is None:
# #             return jsonify({'error': 'Calibration failed'}), 400
        
# #         return jsonify({'pixels_per_cm': PIXELS_PER_CM})
# #     except Exception as e:
# #         logging.error(f"Error during calibration: {str(e)}", exc_info=True)
# #         return jsonify({'error': 'An error occurred during calibration'}), 500

# # @app.route('/process_image', methods=['POST'])
# # def process_image_route():
# #     try:
# #         data = request.get_json()
# #         image_data = base64.b64decode(data['image'].split(',')[1])
# #         np_arr = np.frombuffer(image_data, np.uint8)
# #         image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

# #         global PIXELS_PER_CM
# #         if PIXELS_PER_CM is None:
# #             return jsonify({'error': 'Calibration is required before processing images'}), 400

# #         result = process_image(image, PIXELS_PER_CM)
        
# #         if result is None:
# #             return jsonify({'error': 'Object could not be detected in the image'}), 400

# #         # Convert NumPy types to standard Python types
# #         serializable_result = {
# #             'dimensions': {
# #                 'length': float(result['length']),
# #                 'width': float(result['width']),
# #                 'height': float(result['height'])
# #             },
# #             'volume': float(result['volume'])
# #         }

# #         # Convert processed image to base64
# #         _, buffer = cv2.imencode('.png', result['processed_image'])
# #         processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
# #         serializable_result['processed_image'] = f"data:image/png;base64,{processed_image_base64}"

# #         # Save result to database
# #         new_result = Result(
# #             length=int(result['length']),
# #             width=int(result['width']),
# #             height=int(result['height']),
# #             volume=int(result['volume']),
# #             processed_image=processed_image_base64  # Save only the base64 string
# #         )
# #         db.session.add(new_result)
# #         db.session.commit()

# #         return jsonify(serializable_result)
# #     except Exception as e:
# #         logging.error(f"Error processing image: {str(e)}", exc_info=True)
# #         return jsonify({'error': 'An error occurred while processing the image'}), 500

# # @app.route('/history')
# # def history():
# #     results = Result.query.order_by(Result.created_at.desc()).all()
# #     return render_template('history.html', results=results)

# # @app.route('/camera_test')
# # def camera_test():
# #     return send_file('test_cam.html')

# # if __name__ == '__main__':
# #     create_tables()

# #     # Start the Flask server in a new thread
# #     from threading import Thread

# #     def run_flask_app():
# #         context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# #         context.load_cert_chain('cert.pem', 'key.pem')
# #         app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)

# #     flask_thread = Thread(target=run_flask_app)
# #     flask_thread.start()

# #     # Wait for the server to start
# #     time.sleep(5)  # Adjust this value if necessary

# #     # Perform calibration on app startup
# #     global PIXELS_PER_CM
# #     calibration_result = None
# #     retry_attempts = 5
# #     for attempt in range(retry_attempts):
# #         try:
# #             calibration_result = perform_calibration(
# #                 image_path=r'C:\Users\leodo\Desktop\cube_calculator\calibration9.jpeg',
# #                 known_width_cm=8.56,
# #                 server_url='https://192.168.1.103:5000'
# #             )
# #             if calibration_result:
# #                 PIXELS_PER_CM = calibration_result['pixels_per_cm']
# #                 break
# #         except requests.exceptions.ConnectionError:
# #             logging.error(f"Connection error during calibration attempt {attempt + 1}")
# #             time.sleep(5)

# #     if not calibration_result:
# #         logging.error("Failed to calibrate after multiple attempts")
# #         exit(1)

# #     # Join the Flask server thread to keep the main thread alive
# #     flask_thread.join()







# import ssl
# from flask import Flask, request, render_template, jsonify, send_file
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# import base64
# import cv2
# import numpy as np
# import logging
# from sqlalchemy.dialects.mysql import LONGTEXT
# import subprocess
# import os

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:aaaaaaaaaa@localhost/cube_calculator'
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# PIXELS_PER_CM = None  # Initialize as None to be set after calibration

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# class Result(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     length = db.Column(db.Integer, nullable=False)
#     width = db.Column(db.Integer, nullable=False)
#     height = db.Column(db.Integer, nullable=False)
#     volume = db.Column(db.Integer, nullable=False)
#     processed_image = db.Column(LONGTEXT, nullable=True)
#     created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# def create_tables():
#     with app.app_context():
#         db.create_all()

# @app.route('/')
# def index():
#     venv_activate = os.path.join(os.getcwd(), 'venv', 'Scripts', 'activate')
#     result = subprocess.run(f'{venv_activate} && python calibration.py', shell=True, capture_output=True, text=True)
#     if result.returncode != 0:
#         logging.error("Calibration failed")
#         logging.error(result.stdout)
#         logging.error(result.stderr)
#         exit(1)
#     else:
#         logging.info("Calibration completed successfully")
#         logging.info(result.stdout)
#     return render_template('index.html')

# def process_image(image, pixels_per_cm=None):
#     try:
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
#         # Edge detection
#         edges = cv2.Canny(blurred, 50, 150)
        
#         # Find contours
#         contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
#         if not contours:
#             logging.error("No contours found")
#             return None
        
#         # Find the largest contour (assuming it's the shoe)
#         shoe_contour = max(contours, key=cv2.contourArea)

#         # Get bounding rectangle
#         shoe_rect = cv2.minAreaRect(shoe_contour)
#         box = cv2.boxPoints(shoe_rect)
#         box = np.int32(box)  # Changed from np.int0 to np.int32

#         # Get shoe dimensions in pixels
#         (width, height) = shoe_rect[1]
#         shoe_length = max(width, height)
#         shoe_width = min(width, height)
#         shoe_height = shoe_width * 0.3  

#         if pixels_per_cm is None or pixels_per_cm <= 0:
#             logging.error("Invalid pixels_per_cm value")
#             return None

#         # Convert dimensions to cm using pixels_per_cm
#         shoe_length /= pixels_per_cm
#         shoe_width /= pixels_per_cm
#         shoe_height /= pixels_per_cm

#         volume = shoe_length * shoe_width * shoe_height

#         # Draw contour on the original image
#         cv2.drawContours(image, [box], 0, (0, 255, 0), 2)

#         # Ensure the image is in BGR format
#         if len(image.shape) == 2:  # If grayscale, convert to BGR
#             image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

#         return {
#             'length': round(shoe_length, 1),
#             'width': round(shoe_width, 1),
#             'height': round(shoe_height, 1),
#             'volume': round(volume, 1),
#             'processed_image': image
#         }
#     except Exception as e:
#         logging.error(f"Error processing image: {e}", exc_info=True)
#         return None

# def calibrate(calibration_image, known_width_cm):
#     try:
#         result = process_image(calibration_image, pixels_per_cm=1)  # Temporarily set to 1 for raw pixel value
#         if result is None:
#             logging.error("Calibration failed: No object detected")
#             return None

#         detected_width_pixels = result['width']
#         if detected_width_pixels <= 0:
#             logging.error("Invalid detected width in pixels")
#             return None

#         pixels_per_cm = detected_width_pixels / known_width_cm
#         logging.info(f"Calibration successful: {pixels_per_cm} pixels per cm")
#         return pixels_per_cm
#     except Exception as e:
#         logging.error(f"Error during calibration: {e}", exc_info=True)
#         return None

# @app.route('/calibrate', methods=['POST'])
# def calibrate_route():
#     try:
#         data = request.get_json()
#         image_data = base64.b64decode(data['image'].split(',')[1])
#         known_width_cm = float(data['known_width_cm'])
#         np_arr = np.frombuffer(image_data, np.uint8)
#         image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         global PIXELS_PER_CM
#         PIXELS_PER_CM = calibrate(image, known_width_cm)
        
#         if PIXELS_PER_CM is None:
#             return jsonify({'error': 'Calibration failed'}), 400
        
#         return jsonify({'pixels_per_cm': PIXELS_PER_CM})
#     except Exception as e:
#         logging.error(f"Error during calibration: {str(e)}", exc_info=True)
#         return jsonify({'error': 'An error occurred during calibration'}), 500

# @app.route('/process_image', methods=['POST'])
# def process_image_route():
#     try:
#         data = request.get_json()
#         image_data = base64.b64decode(data['image'].split(',')[1])
#         np_arr = np.frombuffer(image_data, np.uint8)
#         image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#         global PIXELS_PER_CM
#         if PIXELS_PER_CM is None:
#             return jsonify({'error': 'Calibration is required before processing images'}), 400

#         result = process_image(image, PIXELS_PER_CM)
        
#         if result is None:
#             return jsonify({'error': 'Object could not be detected in the image'}), 400

#         # Convert NumPy types to standard Python types
#         serializable_result = {
#             'dimensions': {
#                 'length': float(result['length']),
#                 'width': float(result['width']),
#                 'height': float(result['height'])
#             },
#             'volume': float(result['volume'])
#         }

#         # Convert processed image to base64
#         _, buffer = cv2.imencode('.png', result['processed_image'])
#         processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
#         serializable_result['processed_image'] = f"data:image/png;base64,{processed_image_base64}"

#         # Save result to database
#         new_result = Result(
#             length=int(result['length']),
#             width=int(result['width']),
#             height=int(result['height']),
#             volume=int(result['volume']),
#             processed_image=processed_image_base64  # Save only the base64 string
#         )
#         db.session.add(new_result)
#         db.session.commit()

#         return jsonify(serializable_result)
#     except Exception as e:
#         logging.error(f"Error processing image: {str(e)}", exc_info=True)
#         return jsonify({'error': 'An error occurred while processing the image'}), 500

# @app.route('/history')
# def history():
#     results = Result.query.order_by(Result.created_at.desc()).all()
#     return render_template('history.html', results=results)

# @app.route('/camera_test')
# def camera_test():
#     return send_file('test_cam.html')

# if __name__ == '__main__':
#     create_tables()

#     context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     context.load_cert_chain('cert.pem', 'key.pem')
#     app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)

