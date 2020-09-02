# app.py
from flask import Flask, request, Response, jsonify
from functools import wraps
from pymongo import MongoClient
from exceptions import Unauthorized, BadRequest
from auth import Credentials
from datetime import datetime
import jsonpickle
import numpy as np
import hashlib
import re
import cv2
import subprocess
import string

app = Flask(__name__)
app.config.from_object('config')
client = MongoClient(app.config["MONGO_URI"])
db = client["admin"]

@app.errorhandler(Unauthorized)
def handle_invalid_usage(error):
    response = jsonpickle.encode(error.to_dict())
    return Response(response=response, status=error.status_code, mimetype="application/json")
    
@app.errorhandler(BadRequest)
def handle_invalid_usage2(error):
    response = jsonpickle.encode(error.to_dict())
    return Response(response=response, status=error.status_code, mimetype="application/json")

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = request
        creds = Credentials(r.authorization.username, r.authorization.password)
        user = db.users.find_one({ "username":  creds.username })
        if user is None:
            raise BadRequest('No user associated with the provided username')
        if user["password"] != creds.password:
            raise BadRequest('Password is incorrect')
        return f(*args, **kwargs)
    return decorated_function

def construct_call_str(img_path):
    return 'python ' + app.config["IMG_PROCESS_PATH"] + 'global_classifier.py --model_path ' + app.config["IMG_PROCESS_PATH"] +  r'weights\global.pth --input_path ' + img_path


@app.route('/image/upload', methods=['POST'])
@authenticate
def image_upload():
    r = request
    raise BadRequest('Authenticated!')
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # get by millisecond instead
    now = datetime.now()
    hash_str = now.strftime("%m/%d/%Y, %H:%M:%S") + r.authorization.username
    img_name = hashlib.sha224(hash_str.encode('utf-8')).hexdigest() + ".jpg"
    img_path = app.config["BASE_IMAGE_PATH"] + r.authorization.username
    cv2.imwrite(img_path, img)
    #proc = subprocess.Popen(args=construct_call_str(img_path).split(), stdout=subprocess.PIPE, cwd=app.config["IMG_PROCESS_PATH"])
    #proc.wait()
    #if no errors
    #stdout = proc.stdout.read().decode('utf-8')
    #fake_chance = re.findall(r'[0-9]+', stdout)
    response = {'fake_chance': 99}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/users/create', methods=['POST'])
def users_create():
    data = request.get_json()
    if not "username" in data or data["username"] == "":
        raise BadRequest('A username must be provided')
    if not "password" in data or data["password"] == "":
        raise BadRequest('A password must be provided')
    print(db.users.find_one({ "username":  data["username"] }))
    if not db.users.find_one({ "username":  data["username"] }) is None:
        raise BadRequest('Username provided already exists')
    db.users.insert_one({"username": data["username"], "password": data["password"]})
    return Response(status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)