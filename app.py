from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ffmpeg
import os
import uuid

app = Flask(__name__)
CORS(app)

# 100MB ლიმიტი 1080p ვიდეოებისთვის
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert():
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['video']
    unique_id = str(uuid.uuid4())
    
    # ვიღებთ ორიგინალ გაფართოებას (მაგ: mov, mp4, avi)
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'mp4'
    
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_in.{ext}")
    output_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_out.mp4") # გამოსვლა უეჭველი mp4 რჩება
    
    file.save(input_path)

    try:
        in_file = ffmpeg.input(input_path)
        
        # 1. ვიდეოს ნაკადის დამუშავება: დაკროპვა და 1080p-ზე აწევა
        video = in_file.video.filter('crop', 'ih*9/16', 'ih').filter('scale', 1080, 1920)
        
        # 2. ხმის ნაკადის ცალკე აღება (რომ არ დაიკარგოს)
        audio = in_file.audio
        
        # 3. შეერთება და სწრაფი რენდერი
        ffmpeg.output(
            video,
            audio,
            output_path,
            vcodec='libx264',
            acodec='aac',          # უნივერსალური აუდიო კოდეკი (ხმის გარანტია)
            audio_bitrate='128k',  # სტანდარტული, სუფთა ხმის ხარისხი
            preset='ultrafast',    # მაქსიმალური სისწრაფე
            crf=23,                # ოქროს შუალედი ხარისხსა და ზომას შორის
            threads=2,             # იცავს სერვერს გადატვირთვისა და გათიშვისგან
            movflags='faststart',
            pix_fmt='yuv420p'
        ).run(overwrite_output=True)
        
        return send_file(output_path, as_attachment=True)
        
    except ffmpeg.Error as e:
        # ეს ლოგებში ზუსტად დაგვანახებს, თუ რამე პრობლემა შეიქმნა
        print("FFmpeg Error:", e.stderr.decode('utf8') if e.stderr else str(e))
        return jsonify({"error": "Video processing failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # დროებითი ფაილის წაშლა, რომ სერვერი არ გაივსოს
        if os.path.exists(input_path): 
            os.remove(input_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
