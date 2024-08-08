import os
import ssl
import time
import socket
from app import app, create_tables
from calibration import perform_calibration
from threading import Thread
import signal

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be reachable
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def calibrate(server_url):
    image_path = 'C:/Users/leodo/Desktop/cube_calculator/calibration.jpeg'
    known_width_cm = 9.56
    result = perform_calibration(image_path, known_width_cm, server_url)
    if not result:
        print("Calibration failed")
        exit(1)
    else:
        print("Calibration completed successfully")
        global PIXELS_PER_CM
        PIXELS_PER_CM = result['pixels_per_cm']
        print(result)

def run_flask_app(local_ip):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host=local_ip, port=5000, ssl_context=context, debug=False, use_reloader=False)

if __name__ == '__main__':
    create_tables()

    local_ip = get_local_ip()

    flask_thread = Thread(target=run_flask_app, args=(local_ip,))
    flask_thread.start()

    # Wait for the server to start
    time.sleep(5)  # Adjust this value if necessary

    # Perform calibration on app startup
    server_url = f'https://{local_ip}:5000'
    calibrate(server_url)

    def signal_handler(sig, frame):
        print('Shutting down gracefully...')
        flask_thread.join(timeout=1)  # Adjust timeout as needed
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Keep the main thread alive to handle signals
    while flask_thread.is_alive():
        time.sleep(1)
