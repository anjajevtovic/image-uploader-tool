#!/usr/bin/env python3

'''
    -Image Upload Tool (UNIX only):
        - uploads images with description to MongoDB
        - lists all images stored in DB
        - downloads selected image from DB

    - Start command: gunicorn -b 127.0.0.1:4000 main:app
'''

import json
import logging
import os
import sys

from flask import Flask, request
import pymongo
from pymongo.errors import ConnectionFailure
import gridfs
from gridfs.errors import FileExists

logging.basicConfig(filename='logs', level=logging.INFO)

app = Flask(__name__)

# Loading configuration
CONF_PATH = "config"
if os.path.exists(CONF_PATH):
    with open(CONF_PATH, 'r', encoding='utf-8') as config_file:
        conf = json.loads(config_file.read())
else:
    sys.exit(2)

# Connecting to MongoDB based on a connection string from config file
try:
    conn_str = conf['conn_str']
    db_client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

    db = db_client.images
    fs = gridfs.GridFS(db)
    fs_files = db.fs.files

except ConnectionFailure as conn_fail_msg:
    logging.error('Creating connection with db failed'.join(str(conn_fail_msg)))


@app.route('/')
def home():
    '''
        - This call is returning the name of the application on
        home route.
    '''
    return 'Image Uploader Tool'


@app.route('/upload/', methods=['POST'])
def upload_image():
    '''
        - This call uploads an image based on the data passed in the request
        body to the database

        - Body should be in format of json with following parameters: filename,
        description, path.
            - filename -> name of the image with extension under which it
            should be saved to db
            - description -> description of the image
            - path -> full path from the local system to the image file
    '''
    request_data = request.get_json()

    if request_data is not None and 'filename' in request_data and\
                                    'description' in request_data and\
                                    'path' in request_data:
        filename = request_data['filename']
        desc = request_data['description']
        file_path = request_data['path']
    else:
        return 'Unexpected request body data.'

    entry = fs_files.find_one({'filename': filename})
    if entry is None:
        try:
            with open(file_path, 'rb') as image_file:
                content = image_file.read()

            if content is not None:
                fs.put(content, filename=filename, description=desc)

        except OSError as os_err_msg:
            logging.error('Reading image file failed.'.join(str(os_err_msg)))
        except FileExists as grid_fs_err:
            logging.error('Uploading image to db failed.'.join(str(grid_fs_err)))
    else:
        return 'File with that name already exists in the database.'

    return 'Thank you, you have successfully uploaded your image.'


@app.route('/list/')
def list_all_images():
    '''
        - This call returns names and matching descriptions of all images
        stored in the db.
    '''
    images_list = []
    try:
        cursor = db.fs.files.find({})
        for doc in cursor:
            filename = doc['filename']
            desc = doc['description']
            images_list.append({filename: desc})

    except TypeError as type_err_msg:
        logging.error('Listing conntent failed.'.join(str(type_err_msg)))

    response = json.dumps(images_list)
    return response


@app.route('/download')
def download_image():
    '''
        - This call downloads the image from db to Downloads folder located
        homedirctory directory.
        - GET request must contain parameter specifying which file should be
        downlaoded.
            -  Example: /download?filename=dice.png
    '''
    filename = request.args.get('filename')

    try:
        entry = fs_files.find_one({'filename': filename})
        if entry is not None:
            image_id = entry['_id']

            download = fs.get(image_id).read()
            userdir = os.path.expanduser('~')
            path = userdir + f'/Downloads/{filename}'
            with open(path, 'wb') as image_file:
                image_file.write(download)
    except OSError as os_err_msg:
        logging.error('Such file doesn\'t exist or download failed.'
                      .join(str(os_err_msg)))

    return 'Image is successfully downloaded.'


if __name__ == '__main__':
    app.run()
