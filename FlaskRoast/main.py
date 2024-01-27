from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
from deepface import DeepFace
import praw
import cv2
import numpy as np
 
app = Flask(__name__)
UPLOAD_FOLDER = 'static/files/'
 
app.secret_key = "" #Don't Show
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     

@app.route('/')
def home():
    messages = []
    return render_template('index.html', messages=messages)
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(filename)
        image = cv2.imread(UPLOAD_FOLDER + filename)

        similarity = 0
        post = None

        client_id = '' # Don't show
        client_secret = '' #Don't show
        user_agent = '' #Don't show
        username = "" #Don't show
        password = "" #Don't show

        reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent, username = username, password = password)
        subred = reddit.subreddit("RoastMe").new(limit = 10)

        for i in subred:
            if(i.thumbnail != 'nsfw'):
                req = urllib.request.urlopen(i.thumbnail)
                arr = np.array(bytearray(req.read()), dtype=np.uint8)
                curr_img = cv2.imdecode(arr, -1)

                curr_sim = DeepFace.verify(image, curr_img, enforce_detection = False)['distance']

                if curr_sim > similarity :
                    similarity = curr_sim
                    post = i

        one = None
        two = None
        three = None
        four = None

        if post.comments[0].ups > post.comments[1].ups:
            one = post.comments[0].body
            two = post.comments[1].body
            three = post.comments[2].body
            four = post.comments[3].body
        else:
            one = post.comments[1].body
            two = post.comments[2].body
            three = post.comments[3].body
            four = post.comments[4].body
        flash(one)
        flash(two)
        flash(three)
        flash(four)

        messages = [one, two, three, four]

        return render_template('index.html', filename=filename, messages=messages)
    else:
        flash('Allowed image types are - png and jpg')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='files/' + filename), code=301)
 
if __name__ == "__main__":
    app.run()