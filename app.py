from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route("/index", methods=["GET"])
def index():
    return ""

@app.route("/journal", methods= ["POST"])
def createjounal():
    timestamp = request.form.get("timestamp")
    content = request.form.get("content", "")
    content = content.strip()
    content = content.replace("\'", "")

    cmd = "jrnl '%s : %s'" % (timestamp, content)
    os.system(cmd)
    return ""

@app.route("/journal", methods= ["GET"])
def getjournal():
    cmd = "jrnl  --export json"
    strresult = os.popen(cmd).read()
    result = json.loads(strresult)
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=55180, threaded=True)