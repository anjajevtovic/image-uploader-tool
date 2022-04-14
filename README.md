# Image Uploader 

This tool is based on Flask/Python and MongoDB. It has the following functionalities:
    1. uploading an image with a description to MongoDB using GridFS
    2. list all images with their description
    3. downloading selected image

### How to run the tool

##### Requirements:
    1. python3 installed on the system
    2. running MongoDB with correctly formated URI -> [docs](https://www.mongodb.com/docs/manual/reference/connection-string/); MongoDB can be locally run or in the cloud
    3. UNIX based OS

`config` file has URI for locally set MongoDB as default, it should be edited accordingly as per use case.

##### Commands to run the script:
```
    git clone https://github.com/anjajevtovic/image-uploader-tool.git
    cd image-uploader-tool
    python3 -m pip install -r requirements.txt
    gunicorn -b 127.0.0.1:4000 main:app
```

### Usage

The recommended way to use it is via POSTMAN or any other tool convenient for making HTTP requests. The tool is in the form of API at the moment with the frontend yet to be implemented.

In the project folder, there is **image-upload-tool.postman_collection.json** with the example requests.

##### Endpoints:
    1. **/upload/** - POST request with body in format of json; neccesary json keys: `filename`, `description`, `path`
    2. **/list/** - GET request
    3. **/download** - GET request with `filename` parameter (Example: `/download?filename=cisco.png`)

Image is being downloaded to the `/Downloads` directory of the currently active user

### Additional info:

Logging is turned on by default, once the script is run `logs` file is created, and every error or exception that occurs can be found here.