from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import tempfile

app = Flask(__name__, static_folder='.')
CORS(app)

# Serve the frontend
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        video_url = data.get('url')
        quality = data.get('quality', 'highest')
        
        if not video_url:
            return jsonify({'error': 'URL is required'}), 400
        
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': get_format_string(quality),
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
        
        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_format_string(quality):
    quality_map = {
        'highest': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
        '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]',
        '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]',
        '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]',
    }
    return quality_map.get(quality, quality_map['highest'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)