from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define PII patterns
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b(?:\+91[-\s]?|0)?[6789]\d{9}\b",
    "pan": r"[A-Z]{5}[0-9]{4}[A-Z]"
}

@app.route("/detect_pii", methods=["POST"])
def detect_pii():
    file = request.data
    npimg = np.frombuffer(file, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    results = []
    d = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    for i in range(len(d['text'])):
        text = d['text'][i].strip()
        if not text:
            continue
        for label, pattern in PII_PATTERNS.items():
            if re.fullmatch(pattern, text):
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                results.append({
                    "left": int(x),
                    "top": int(y),
                    "right": int(x + w),
                    "bottom": int(y + h),
                    "type": label
                })
                break

    return jsonify(results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
