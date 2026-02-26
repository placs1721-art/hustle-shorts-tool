from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ffmpeg
import os
import uuid

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB-მდე გავზარდოთ

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert():
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['video']
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_in.mp4")
    output_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_out.mp4")
    
    file.save(input_path)

    try:
        # 1080p Shorts ფორმატი [cite: 2026-02-26]
        (
            ffmpeg
            .input(input_path, t=60)
            .filter('crop', 'ih*9/16', 'ih')
            .filter('scale', 1080, 1920) 
            .output(
                output_path, 
                vcodec='libx264', 
                crf=20, # მაღალი ხარისხი [cite: 2026-02-26]
                preset='ultrafast', # სისწრაფისთვის უფასო სერვერზე [cite: 2026-02-26]
                movflags='faststart',
                pix_fmt='yuv420p',
                threads=0 # იყენებს ყველა ხელმისაწვდომ ბირთვს [cite: 2026-02-26]
            )
            .run(overwrite_output=True)
        )
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path): os.remove(input_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
