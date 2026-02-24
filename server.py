import http.server
import json
import os
import sys
from datetime import datetime

PORT = 8000
# Get the absolute path of the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'orders.db.json')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

class OrderHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def translate_path(self, path):
        # Serve from the public directory
        path = super().translate_path(path)
        rel_path = os.path.relpath(path, os.getcwd())
        return os.path.join(PUBLIC_DIR, rel_path)

    def do_GET(self):
        if self.path == '/api/orders':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if not os.path.exists(DB_FILE):
                with open(DB_FILE, 'w') as f:
                    json.dump([], f)
            with open(DB_FILE, 'r') as f:
                self.wfile.write(f.read().encode())
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/orders':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                new_order = json.loads(post_data.decode())
                
                new_order['id'] = str(int(datetime.now().timestamp() * 1000))
                new_order['timestamp'] = datetime.now().isoformat()

                orders = []
                if os.path.exists(DB_FILE):
                    try:
                        with open(DB_FILE, 'r') as f:
                            orders = json.load(f)
                    except:
                        orders = []
                
                orders.append(new_order)
                with open(DB_FILE, 'w') as f:
                    json.dump(orders, f, indent=2)
                
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Success"}).encode())
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(str(e).encode())

    def do_DELETE(self):
        if self.path == '/api/orders':
            with open(DB_FILE, 'w') as f:
                json.dump([], f)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Cleared"}).encode())

if __name__ == '__main__':
    print(f"--- GOURMET HUB SERVER ---")
    print(f"1. Open your browser to: http://localhost:{PORT}")
    print(f"2. To order from other devices (phones, laptops), use your IP address:")
    print(f"   Example: http://192.168.1.5:{PORT}")
    print(f"--------------------------")
    
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, OrderHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
