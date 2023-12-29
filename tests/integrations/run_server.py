from tests.integrations.setup.setup_test_server import setup_test_server


if __name__ == "__main__":
    httpd = setup_test_server()
    print("Serving at port 8000")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping test server")
        httpd.shutdown()
