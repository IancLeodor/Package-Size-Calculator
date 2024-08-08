import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't need to be reachable; just used to get the local IP
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"Local IP Address: {local_ip}")
