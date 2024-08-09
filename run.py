import os
import ssl
import time
import argparse
from app import app, create_tables
from calibration import perform_calibration
from threading import Thread
import signal

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Flask app with calibration")
    parser.add_argument('--image_path', type=str, default='calibration.jpeg', help="Path to the calibration image")
    parser.add_argument('--known_width_cm', type=float, default=7, help="Known width of the object in cm")
    parser.add_argument('--server_url', type=str, default='https://localhost:5000', help="URL of the server for calibration")
    parser.add_argument('--cert_file', type=str, default='cert.pem', help="Path to the SSL certificate file")
    parser.add_argument('--key_file', type=str, default='key.pem', help="Path to the SSL key file")
    parser.add_argument('--host', type=str, default='0.0.0.0', help="Host to run the Flask app")
    parser.add_argument('--port', type=int, default=5000, help="Port to run the Flask app")
    return parser.parse_args()

def calibrate(image_path, known_width_cm, server_url):
    result = perform_calibration(image_path, known_width_cm, server_url)
    if not result:
        print("Calibration failed")
        exit(1)
    else:
        print("Calibration completed successfully")
        global PIXELS_PER_CM
        PIXELS_PER_CM = result['pixels_per_cm']
        print(result)

def run_flask_app(host, port, cert_file, key_file):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    app.run(host=host, port=port, ssl_context=context, debug=False, use_reloader=False)

def main():
    args = parse_args()

    create_tables()

    flask_thread = Thread(target=run_flask_app, args=(args.host, args.port, args.cert_file, args.key_file))
    flask_thread.start()

    time.sleep(5)

    calibrate(args.image_path, args.known_width_cm, args.server_url)

    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        flask_thread.join(timeout=1)
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while flask_thread.is_alive():
        time.sleep(1)

if __name__ == '__main__':
    main()
