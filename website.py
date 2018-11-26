# -*- coding: utf-8 -*-
import os
from PIL import Image
from flask import Flask, request, url_for, send_from_directory,render_template, flash
from werkzeug import secure_filename
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from PIL import Image
from scipy.misc import imread,imsave
import matplotlib.pyplot as plt
import numpy as np

DEBUG = True
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
background = Image.open("import2.jpg")

html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta charset=utf-8 />
<title>Image Encyption Website</title>
<style>
/* Fonts */
@import url(https://fonts.googleapis.com/css?family=Abril+Fatface);
@import url(https://fonts.googleapis.com/css?family=Amatic+SC);
/* Mixins */
/* Base Styles */
* {
  box-sizing: border-box; }

html, body {
  color: #999999;
  font-family: Helvetica, Arial, sans-serif;
  font-size: 10px;
  font-weight: 100;
  margin: 0;
  padding: 0; }

.container {
  margin: 0 auto;
  max-width: 750px;
  padding: 0 24px; }

header {
  animation: bgFadeIn 1s ease-in both;
  position: relative;
  padding: 28px;
  text-align: center; }
  header:before {
    background: linear-gradient(rgba(0, 235, 235, 0.7), rgba(0, 235, 235, 0.7)), url("http://www.dyxzjw.com/uploadfile/image/20170629/2017062917100122122.png");
    background-color: #CCCCCC;
    background-attachment: fixed;
    background-position: center center;
    background-repeat: no-repeat;
    -webkit-background-size: cover;
    -moz-background-size: cover;
    -o-background-size: cover;
    background-size: cover;
    bottom: 0;
    content: ' ';
    left: 0;
    position: absolute;
    right: 0;
    top: 0;
    z-index: -1; }
@keyframes bgFadeIn {
  0% {
    background-color: white; }
  100% {
    background-color: rgba(255, 255, 255, 0); } }
  header .container {
    margin: 12rem auto; }
  header h1 {
    border-bottom: 2px solid #FFFFFF;
    border-top: 2px solid #FFFFFF;
    color: #FFFFFF;
    font-family: "Amatic SC", cursive;
    font-size: 8.75rem;
    margin: 0; }
  header h3 {
    color: #FFF0A5;
    font-family: "Abril Fatface", cursive;
    font-size: 3.75rem;
    font-style: italic;
    font-weight: 100;
    margin: 0; }

section {
  padding: 2rem; }
  section p {
    font-size: 2.5rem;
    line-height: 3.5rem;
    color: #808080; }
    section p.lead-in {
      font-size: 3rem;
      color: #444; }
      section p.lead-in:first-letter {
        font-size: 7.25rem;
        display: block;
        float: left;
        position: relative;
        line-height: .1;
        top: -0.200em; }

/*# sourceMappingURL=style.css.map */


</style>
</head>
<body>
    <header>
    <div class="container">
    <h1>Numerical Computing &nbsp Final Project</h1>
    <h3>Wenlin Gong</h3>
	<h3>2018 Fall</h3>
    </div><!-- /.container -->
    </header>
     <section>
    <div class="container">
    <p class="lead-in">Want to encrypt your NC homework? Here's how!</p>
	<p><br></p>
        <p>Enter the last four digit of your RIN</p>
        <input type="text" name=text />
	<p>Upload a image you want to encrypt</p>
        <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=Upload>
        </from>      
	<p>Encrypted Image</p>
    </div><!-- /.container -->
</section>
</body>
</html>
"""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    img = Image.open(filename)
    background = Image.open("import2.jpg")
    width, height = img.size
    backg_width = 2120
    backg_height = 1414
    
    # crop the center part of the background
    corner1 = round((backg_width - width)*0.5),round((backg_height - height)*0.5)
    corner2 = round((backg_width - width)*0.5)+width,round((backg_height - height)*0.5)+height
    background_crop = background.crop((corner1[0],corner1[1],corner2[0],corner2[1]))
    
    # kaotic sequence
    key = -0.40001
    L = max(width,height)
    x=[key]
    y=[key]
    alpha = 1.4
    beta = 0.3  
    for i in range(L):
        x.append(1-alpha*x[-1]*x[-1]+y[-1])
        y.append(beta*x[-1])
    x[width:len(x)]=[]
    y[height:len(y)]=[]
    
    #store index
    x_index = []
    y_index = []
    x_sort = sorted(x)
    y_sort = sorted(y)
    
    for i in range(width):
        x_index.append(x_sort.index(x[i]))
    for i in range(height):
        y_index.append(y_sort.index(y[i]))
    
    # open pixelMap to make changes
    img_pixelMap = img.load()
    # img2 is a copy of img
    img2 = np.zeros([width,height,3],dtype=np.uint8)
    img2.fill(0)
    backc_pixelMap = background_crop.load()
    for i in range(width):
        for j in range(height):
            img2[i,j] = img_pixelMap[x_index[i],y_index[j]]
    
    # bitshift
    for i in range(width):
        for j in range(height):
            img2[i,j][0] = img2[i,j][0] & 240
            img2[i,j][1] = img2[i,j][1] & 240
            img2[i,j][2] = img2[i,j][2] & 240
    for pixel in background_crop.getdata():
        v0 = (pixel[0]) & 240
        v1 = (pixel[1]) & 240
        v2 = (pixel[2]) & 240
        pixel = (v0,v1,v2)    
    for i in range(width):
        for j in range(height):
            img2[i,j][0] = img2[i,j][0] >> 4
            img2[i,j][1] = img2[i,j][1] >> 4
            img2[i,j][2] = img2[i,j][2] >> 4  
    
    # change background image
    backc_pixelMap = background_crop.load()
    for i in range(width):
        for j in range(height):
            if(img2[i,j][0]>16 or img2[i,j][1]>16 or img2[i,j][2]>16):
                print("error")
            backc_pixelMap[i,j] = (backc_pixelMap[i,j][0]+img2[i,j][0],
                                    backc_pixelMap[i,j][1]+img2[i,j][1],
                                    backc_pixelMap[i,j][2]+img2[i,j][2])
    
    # add the small piece of crop into larger background image
    back_pixelMap = background.load()
    for i in range(width):
        for j in range(height):
            back_pixelMap[i+corner1[0],j+corner1[1]] = backc_pixelMap[i,j]
            
    background.save("py_encrypted.png")    
    img.close()
    filename = "py_encrypted.png"
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            return html + '<br><img src=' + file_url + '>'
    return html

@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename) 


if __name__ == '__main__':
    app.run()
