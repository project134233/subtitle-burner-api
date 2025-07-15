from flask import Flask, request, send_file
import subprocess
import os
import uuid
import requests

app = Flask(__name__)

# Function to download files using Python
def download_file(url, filename):
    print(f"Downloading: {url} -> {filename}")
    response = requests.get(url)
    response.raise_for_status()  # raise error if failed
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

@app.route('/merge', methods=['POST'])
def merge_subtitles():
    video_url = request.form['video_url']
    subtitle_url = request.form['subtitle_url']

    session_id = str(uuid.uuid4())
    video_file = f'{session_id}_input.mp4'
    subtitle_file = f'{session_id}_subs.srt'
    output_file = f'{session_id}_output.mp4'

    try:
        # Download files using Python
        download_file(video_url, video_file)
        download_file(subtitle_url, subtitle_file)

        # Subtitle styling filter
        subtitle_filter = (
            f"subtitles={subtitle_file}:force_style="
            "'FontName=Arial,FontSize=10,PrimaryColour=&H0005DFFF,"
            "OutlineColour=&H00000000,BorderStyle=1,Outline=1'"
        )

        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', video_file,
            '-vf', subtitle_filter,
            '-c:v', 'libx264',
            '-crf', '14', 
            '-preset', 'fast', 
            '-c:a', 'copy',
            output_file
        ]

        print("Running FFmpeg command:", " ".join(cmd))

        subprocess.run(cmd, check=True)

        print(f"FFmpeg completed successfully. Returning file: {output_file}")
        response = send_file(output_file, mimetype='video/mp4')

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return f"Processing error: {str(e)}", 500

    finally:
        cleanup(video_file, subtitle_file, output_file)

    return response

def cleanup(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

app.run(host='0.0.0.0', port=5000)
