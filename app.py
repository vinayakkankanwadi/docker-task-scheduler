from datetime import datetime
import socket

print("=" * 50)
print("Hello World from Docker!")
print(f"Container ID: {socket.gethostname()}")
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)
