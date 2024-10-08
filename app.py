from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Set a directory for temporarily storing downloaded videos
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle video download
@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    video_filename = None  # Initialize the video filename
    
    if not url:
        flash("Please provide a valid Instagram URL.")
        return redirect(url_for('index'))

    if "instagram.com" not in url:
        flash("Please enter a valid Instagram post URL.")
        return redirect(url_for('index'))

    # Scrape the video from Instagram
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the video tag in the HTML
        video_tag = soup.find('meta', property='og:video')
        if not video_tag:
            flash("No video found. Please check the URL and try again.")
            return redirect(url_for('index'))

        video_url = video_tag['content']

        # Download the video temporarily
        video_response = requests.get(video_url)
        video_filename = os.path.join(DOWNLOAD_DIR, 'downloaded_video.mp4')
        with open(video_filename, 'wb') as video_file:
            video_file.write(video_response.content)

        # Serve the video for download
        return send_file(video_filename, as_attachment=True)

    except Exception as e:
        flash(f"An error occurred: {e}")
        return redirect(url_for('index'))

    finally:
        # Clean up the downloaded file after serving if it exists
        if video_filename and os.path.exists(video_filename):
            os.remove(video_filename)

if __name__ == '__main__':
    app.run(debug=True)
