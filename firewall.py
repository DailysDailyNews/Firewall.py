import socket
import threading
import time
from datetime import datetime

class SimpleFirewall:
    def __init__(self, blocked_ports=None, log_file="firewall.log"):
        self.blocked_ports = set(blocked_ports) if blocked_ports else set()
        self.log_file = log_file
        self.running = True

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)
        print(log_entry.strip())

    def handle_connection(self, client_socket, client_address):
        ip_address, port = client_address
        self.log(f"Incoming connection attempt from {ip_address}:{port}")
        client_socket.close()
        self.log(f"Connection from {ip_address}:{port} blocked and closed.")

    def start_listener(self, port):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', port))  # Listen on all interfaces
            server_socket.listen(5)  # Allow up to 5 pending connections
            self.log(f"Listening on port {port}...")

            while self.running:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, client_address))
                client_thread.daemon = True  # Allow the main thread to exit
                client_thread.start()

        except OSError as e:
            self.log(f"Error binding to port {port}: {e}")
        finally:
            if 'server_socket' in locals():
                server_socket.close()
                self.log(f"Stopped listening on port {port}.")

    def run(self, ports_to_monitor):
        threads = []
        for port in ports_to_monitor:
            if port in self.blocked_ports:
                self.log(f"Warning: Port {port} is in the blocked list and will still be monitored.")
            thread = threading.Thread(target=self.start_listener, args=(port,))
            threads.append(thread)
            thread.start()

        try:
            while True:
                time.sleep(1)  # Keep the main thread alive
        except KeyboardInterrupt:
            self.log("Firewall shutting down...")
            self.running = False
            for thread in threads:
                thread.join()  # Wait for all listener threads to finish
            self.log("Firewall stopped.")

if __name__ == "__main__":
    # Define the ports you want to monitor and block incoming connections on
    monitored_ports = [21, 22, 23, 80, 443, 135, 445, 1433, 3306, 3389, 8080]
    # Optionally define specific ports you want to explicitly block (will still be monitored)
    blocked_ports = [135, 445]
    firewall = SimpleFirewall(blocked_ports=blocked_ports)
    firewall.run(monitored_ports)
