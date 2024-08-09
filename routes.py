from flask import request, render_template, jsonify, send_file
import base64
import cv2
import numpy as np
import logging
from app import app, db
from models import Result
from utils import process_image, calibrate

PIXELS_PER_CM = None  

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calibrate', methods=['POST'])
def calibrate_route():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'].split(',')[1])
        known_width_cm = float(data['known_width_cm'])
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        global PIXELS_PER_CM
        PIXELS_PER_CM = calibrate(image, known_width_cm)
        
        if PIXELS_PER_CM is None:
            return jsonify({'error': 'Calibration failed'}), 400
        
        return jsonify({'pixels_per_cm': PIXELS_PER_CM})
    except Exception as e:
        logging.error(f"Error during calibration: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred during calibration'}), 500

@app.route('/process_image', methods=['POST'])
def process_image_route():
    try:
        data = request.get_json()
        image_data = base64.b64decode(data['image'].split(',')[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        global PIXELS_PER_CM
        if PIXELS_PER_CM is None:
            return jsonify({'error': 'Calibration is required before processing images'}), 400

        result = process_image(image, PIXELS_PER_CM)
        
        if result is None:
            return jsonify({'error': 'Object could not be detected in the image'}), 400

        serializable_result = {
            'dimensions': {
                'length': float(result['length']),
                'width': float(result['width']),
                'height': float(result['height'])
            },
            'volume': float(result['volume'])
        }

        _, buffer = cv2.imencode('.png', result['processed_image'])
        processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
        serializable_result['processed_image'] = f"data:image/png;base64,{processed_image_base64}"

        new_result = Result(
            length=int(result['length']),
            width=int(result['width']),
            height=int(result['height']),
            volume=int(result['volume']),
            processed_image=processed_image_base64  
        )
        db.session.add(new_result)
        db.session.commit()

        return jsonify(serializable_result)
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing the image'}), 500

@app.route('/history')
def history():
    results = Result.query.order_by(Result.created_at.desc()).all()
    return render_template('history.html', results=results)

