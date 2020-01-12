# app.py
from flask import Flask, request, Response
import jsonpickle
import numpy as np
import re
import cv2
import subprocess
app = Flask(__name__)


@app.route('/api/test', methods=['POST'])
def test():
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img_path = r'C:\Projects\FALdetector-master\examples\modified.jpg'
    call_str = r'python C:\Projects\FALdetector-master\global_classifier.py --model_path C:\Projects\FALdetector-master\weights\global.pth --input_path ' + img_path
    print(call_str.split())
#subprocess.Popen(['cd', 'C:/Projects/FALdetector-master'], shell=True)
    proc = subprocess.Popen(args=call_str.split(), stdout=subprocess.PIPE, cwd=r'C:\Projects\FALdetector-master')
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