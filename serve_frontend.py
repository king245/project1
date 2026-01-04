import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "frontend_simple"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    # Ensure dependencies like 'os' are used properly if needed or remove if unused. 
    # Here just changing cwd or passing directory to handler.
    # We will pass directory to handler to avoid changing global CWD if possible, 
    # but SimpleHTTPRequestHandler needs directory arg in Python 3.7+
    
    # Check if directory exists
    if not os.path.exists(DIRECTORY):
        print(f"Directory {DIRECTORY} not found!")
        exit(1)

    print(f"Serving {DIRECTORY} at http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
