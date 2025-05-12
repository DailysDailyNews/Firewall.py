import socket
import psutil
import time
import logging
import subprocess

# Configure logging
logging.basicConfig(filename='network_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_active_connections():
    """Lists active network connections with error handling."""
    try:
        connections = psutil.net_connections()
        active = [conn for conn in connections if conn.status == psutil.CONN_ESTABLISHED or conn.status == psutil.CONN_LISTEN]
        return active
    except Exception as e:
        logging.error(f"Error getting active connections: {e}")
        return []

def log_user_action(action, details=None):
    """Logs user initiated actions."""
    message = f"User Action: {action}"
    if details:
        message += f" - {details}"
    logging.info(message)

def block_port(port):
    """Blocks incoming connections on the specified port using ufw."""
    try:
        result = subprocess.run(['sudo', 'ufw', 'deny', 'in', str(port)], capture_output=True, text=True, check=True)
        logging.info(f"Successfully blocked incoming connections on port {port}. Output: {result.stdout.strip()}")
        print(f"Blocked incoming connections on port {port}.")
        log_user_action("Blocked port", details=f"Port: {port}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error blocking port {port} with ufw: {e.stderr.strip()}")
        print(f"Error blocking port {port}. See logs for details.")
    except FileNotFoundError:
        logging.error("ufw command not found. Ensure ufw is installed.")
        print("Error: ufw command not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while blocking port {port}: {e}")
        print(f"An unexpected error occurred while blocking port {port}.")

def unblock_port(port):
    """Unblocks incoming connections on the specified port using ufw."""
    try:
        result = subprocess.run(['sudo', 'ufw', 'delete', 'deny', 'in', str(port)], capture_output=True, text=True, check=True)
        logging.info(f"Successfully unblocked incoming connections on port {port}. Output: {result.stdout.strip()}")
        print(f"Unblocked incoming connections on port {port}.")
        log_user_action("Unblocked port", details=f"Port: {port}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error unblocking port {port} with ufw: {e.stderr.strip()}")
        print(f"Error unblocking port {port}. See logs for details.")
    except FileNotFoundError:
        logging.error("ufw command not found. Ensure ufw is installed.")
        print("Error: ufw command not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while unblocking port {port}: {e}")
        print(f"An unexpected error occurred while unblocking port {port}.")

def should_block(connection):
    """
    Placeholder function to determine if a connection warrants blocking.
    Implement your logic here. For example, you might check for:
    - New listening ports that you don't recognize.
    - Repeated connection attempts from a specific IP.
    - Connections on unusual ports.
    """
    # Example: Block any new listening port (you'll likely want more sophisticated logic)
    if connection.status == psutil.CONN_LISTEN:
        # Add logic to check if this is a known/expected listening port
        known_ports = [22, 80, 443] # Example of your expected listening ports
        if connection.laddr.port not in known_ports:
            return True
    return False

if __name__ == "__main__":
    print("Network monitoring started. Press Ctrl+C to stop.")
    log_user_action("Monitoring started")
    blocked_ports = set()  # Keep track of blocked ports

    try:
        while True:
            active_connections = get_active_connections()
            print("Active Network Connections:")
            current_listening_ports = set()

            for conn in active_connections:
                try:
                    local_address = f"{conn.laddr.ip}:{conn.laddr.port}"
                    remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    status = conn.status
                    print(f"  Local: {local_address}, Remote: {remote_address}, Status: {status}")
                    if status == psutil.CONN_LISTEN:
                        current_listening_ports.add(conn.laddr.port)
                        if should_block(conn) and conn.laddr.port not in blocked_ports:
                            block_port(conn.laddr.port)
                            blocked_ports.add(conn.laddr.port)

                except Exception as e:
                    logging.error(f"Error processing connection details: {e} - {conn}")

            # You might want to add logic here to unblock ports if they are no longer listening
            # or based on other criteria.

            time.sleep(5)  # Check every 5 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        log_user_action("Monitoring stopped by user")
        # Optionally unblock all ports blocked by this script on exit
        if blocked_ports:
            print("Unblocking ports blocked by this script...")
            for port in list(blocked_ports): # Iterate over a copy to allow removal
                unblock_port(port)
                blocked_ports.remove(port)
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
        log_user_action("Unexpected error", details=str(e))
        # Optionally unblock all ports blocked by this script on critical error
        if blocked_ports:
            print("Unblocking ports blocked by this script due to error...")
            for port in list(blocked_ports):
                unblock_port(port)
                blocked_ports.remove(port)
