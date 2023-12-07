import http.server
import socketserver
import threading
import json
import os


def setup_test_server():
    PORT = 8000

    def get_correct_directory():
        current_dir = os.path.dirname(os.path.realpath(__file__))

        backend_dir = os.path.abspath(os.path.join(current_dir, "../../../"))

        directory = os.path.join(
            backend_dir, "tests/integrations/test_data/test_programs/"
        )

        return directory

    DIRECTORY = get_correct_directory()

    class TestRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            http.server.SimpleHTTPRequestHandler.end_headers(self)

        def translate_path(self, path):
            if path.startswith("/api/program/"):
                program_path = path.split("/")[-1]
                file_path = os.path.join(DIRECTORY, f"program_{program_path}.json")
                return file_path
            return http.server.SimpleHTTPRequestHandler.translate_path(self, path)

        def do_GET(self):
            # Serving the JSON file content
            file_path = self.translate_path(self.path)
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                with open(file_path, "rb") as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "File not found")

    httpd = socketserver.TCPServer(("", PORT), TestRequestHandler)

    # Start server in a new thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(f"Test server started at http://localhost:{PORT}")
    return httpd
