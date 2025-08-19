import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

# Set the directory to serve files from
frontend_dir = Path(__file__).parent
os.chdir(frontend_dir)

PORT = 3000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow requests from the frontend to backend
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend server running at: http://localhost:{PORT}")
        print(f"📁 Serving files from: {frontend_dir}")
        print(f"🚀 Make sure your backend is running at: http://127.0.0.1:8000")
        print(f"📖 Opening browser...")
        
        # Open browser automatically
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Frontend server stopped.")
