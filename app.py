from flask import Flask, request, jsonify, render_template
from gallery import get_images
import journal
import json
import os

app = Flask(__name__)

@app.route("/gallery", methods=["GET"])
def render_gallery_page():
    return render_template("gallery.html")

@app.route("/journal", methods=["GET"])
def render_journal_page():
    return render_template("journal.html")

@app.route("/api/gallery/images", methods=["GET"])
def get_image_data():
    return jsonify({
        "images" : get_images()
    })

@app.route("/api/journal", methods= ["POST"])
def createjounal():
    timestamp = request.form.get("timestamp")
    content = request.form.get("content", "")
    content = content.strip()
    content = content.replace("\'", "")

    cmd = "jrnl '%s : %s'" % (timestamp, content)
    os.system(cmd)
    return ""

@app.route("/api/journal", methods= ["GET"])
def get_journal_json():
    result = journal.get_journal()
    return jsonify(result)

@app.route("/api/journal/combined", methods= ["GET"])
def get_combined_journal_json():
    result = journal.get_combined_journal()
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=55180, threaded=True)