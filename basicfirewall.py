import socket
import threading
import logging
from datetime import datetime

#Logging Setup
logging.basicConfig(filename="firewall_logs.txt",
level=logging.INFO,
format="%(asctime)s - %(messages)s") 

#Ports to monitor, suggest to close all ports, and tunnel
PORTS = [80, 443]
HOST = "0.0.0.0" #Listen to all Ports, Socket Plugin's available

def log_attack(ip, user_agent):
   """Log Attacker Activity"""
  log_message = f"Suspicious activity detected from {ip} |
User-Agent: {user_agent}"
  logging.info(log_message)
  print(log_message)

def handle_connection(client_socket, addr):
   """Handles Incoming connections."""
  ip = addr[0]

  try:
  # Clients first Request
    request = 
client_socket.recv(1024).decode(errors="ignore")
    user_agent = "Unknown"

   # Extract User-Agent Info
    for line in request.split("\n):
      if "User-Agent:" in line:
        user_agent =
line.split("User-Agent:")[1].strip()
        break

   #Log Suspicious connections
    log_attack(ip, user_agent)

  except Exception as e:
    print(f"Error handling connection from {ip}: {e}")

  finally:
    client_socket.close()

def start_listner(port):
   """Starts a listner"""
  server =
socket.socket(socket.AF_INET, socket.SOCK_REUSEADDR, 1)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  try:
    server.bind((HOST, port))
    server.listen(5)
    print(f"Listening on port {port}...")

    while True:
      client_socket, addr =
server.accept()

threading.Thread(target=handle_connection, args=(client_socket, addr)).start()

    except Exception as e:
      print(f"Error starting server on port {port}: {e}")

    finally:
      server.close()

#Starts the listner
for port in PORTS:

threading.Thread(target=start_listener, args=(port,)).start()
