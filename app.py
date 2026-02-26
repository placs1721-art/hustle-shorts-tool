from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ffmpeg
import os
import uuid

app = Flask(__name__)
CORS(app)

# მაქსიმალური ზომა 100MB, რომ 1080p ვიდეოებმა თავისუფლად გაიაროს
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "HustleBotics API is Running! 🚀 Ready for 10M views."

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
        # Full HD 1080x1920 კონვერტაცია ხმით
        (
            ffmpeg
            .input(input_path, t=60)
            .filter('crop', 'ih*9/16', 'ih')
            .filter('scale', 1080, 1920) 
            .output(
                output_path, 
                vcodec='libx264', 
                acodec='aac',      # აბრუნებს ხმას
                strict='experimental',
                crf=20,            # მაღალი ვიზუალური ხარისხი
                preset='ultrafast', # სისწრაფე Render-ის უფასო CPU-სთვის
                movflags='faststart',
                pix_fmt='yuv420p',
                threads=0          # იყენებს სერვერის მაქსიმალურ რესურსს
            )
            .run(overwrite_output=True)
        )
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # ფაილების წაშლა ადგილი რომ არ გაივსოს
        if os.path.exists(input_path): os.remove(input_path)
        # შენიშვნა: გამომავალ ფაილს Flask აგზავნის და მერე შეგიძლია წაშალო, 
        # მაგრამ Render-ის დისკი ავტომატურად იწმინდება გადატვირთვისას.

if __name__ == '__main__':
    # პორტის დინამიური აღება Render-ისთვის
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
