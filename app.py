# app.py
from flask import Flask, request, Response
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

def construct_call_str(img_path):
    return 'python ' + app.config["IMG_PROCESS_PATH"] + 'global_classifier.py --model_path ' + app.config["IMG_PROCESS_PATH"] +  r'weights\global.pth --input_path ' + img_path

@app.route('/api/upload', methods=['POST'])
def test():
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # get by millisecond instead
    now = datetime.now()
    hash_str = now.strftime("%m/%d/%Y, %H:%M:%S") + r.authorization.username
    img_name = hashlib.sha224(hash_str.encode('utf-8')).hexdigest() + ".jpg"
    img_path = app.config["BASE_IMAGE_PATH"] + img_name
    cv2.imwrite(img_path, img)
    proc = subprocess.Popen(args=construct_call_str(img_path).split(), stdout=subprocess.PIPE, cwd=app.config["IMG_PROCESS_PATH"])
    proc.wait()
    #if no errors
    stdout = proc.stdout.read().decode('utf-8')
    fake_chance = re.findall(r'[0-9]+', stdout)
    print(fake_chance)
    response = {'fake_chance': fake_chance[0], 'errMsg': ''
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)