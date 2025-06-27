from flask import Flask, render_template, request, send_from_directory
import os
import uuid
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/platform/<platform>')
def platform_page(platform):
    return render_template('platform.html', platform=platform)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    platform = request.form['platform']
    quality = request.form['quality']
    filename = str(uuid.uuid4())
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'outtmpl': filepath + '.%(ext)s',
        'quiet': True,
        'cookiefile': 'youtube_cookies.txt'  # <-- Required for YouTube login-restricted videos
    }

    if quality == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    elif quality == '720p':
        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
    elif quality == '1080p':
        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("▶ Downloading:", url)
            ydl.download([url])
    except Exception as e:
        return f"❌ Download failed: {str(e)}"

    for ext in ['.mp3', '.mp4']:
        final_file = filepath + ext
        if os.path.exists(final_file):
            return send_from_directory(DOWNLOAD_FOLDER, os.path.basename(final_file), as_attachment=True)

    return "❌ File not found after download."

if __name__ == '__main__':
    app.run(debug=True)
