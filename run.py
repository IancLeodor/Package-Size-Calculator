import os
import ssl
import time
from app import app, create_tables
from calibration import perform_calibration
from threading import Thread
import signal

def calibrate():
    image_path = 'C:/Users/leodo/Desktop/cube_calculator/calibration.jpeg'
    known_width_cm = 9.56
    server_url = 'https://192.168.1.103:5000'
    result = perform_calibration(image_path, known_width_cm, server_url)
    if not result:
        print("Calibration failed")
        exit(1)
    else:
        print("Calibration completed successfully")
        global PIXELS_PER_CM
        PIXELS_PER_CM = result['pixels_per_cm']
        print(result)

def run_flask_app():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=False, use_reloader=False)

if __name__ == '__main__':
    create_tables()

    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    time.sleep(5)

    calibrate()

    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        flask_thread.join(timeout=1) 
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while flask_thread.is_alive():
        time.sleep(1)
