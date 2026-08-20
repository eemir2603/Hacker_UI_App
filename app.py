import socket
from flask import Flask, request, jsonify, render_template, send_from_directory
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, template_folder='.') 

# Function to scan a single port
def scan_single_port(target, port):
    scanner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    scanner.settimeout(0.5)
    try:
        result = scanner.connect_ex((target, port))
        if result == 0:
            return f"[+] Port {port} is OPEN"
        return None
    except:
        return None
    finally:
        scanner.close()

# renders HTML
@app.route('/')
def index():
    return render_template('index.html')
# CSS route
@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

# scanning
@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.get_json()
    target_ip = data.get('ip')
    
    #  standart ports
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 3389, 8080]
    open_ports = []

    # Using ThreadPoolExecutor to scan ports concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda p: scan_single_port(target_ip, p), ports_to_scan)
        
    for res in results:
        if res:
            open_ports.append(res)
            
    if not open_ports:
        open_ports.append("[-] No common open ports found.")

    return jsonify({"target": target_ip, "results": open_ports})

if __name__ == '__main__':
    app.run(debug=True, port=5000)