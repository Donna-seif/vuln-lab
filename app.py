from flask import Flask

app = Flask(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Intentionally vulnerable lab: only ever listen on localhost
    app.run(host="127.0.0.1", port=5000, debug=True)
