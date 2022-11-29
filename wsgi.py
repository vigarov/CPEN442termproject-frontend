from backend import app as application
app = application

if __name__ == "__main__":
    app.run(threaded=True, port=5001)