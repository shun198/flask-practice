from flask import Flask

app = Flask(__name__)

@app.route("/api/health")
def hello_world():
    return {"msg": "pass"}
