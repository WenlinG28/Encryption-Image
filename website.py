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
            return "homepage.html" + '<br><img src=' + file_url + '>'
    return "homepage.html"

@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename) 


if __name__ == '__main__':
    app.run()
