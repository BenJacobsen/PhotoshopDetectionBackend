from flask import Flask, request, Response, jsonify
from functools import wraps
import boto3
import base64
from enum import Enum
from pymongo import MongoClient
from exceptions import Unauthorized, BadRequest
import pika
from datetime import datetime
import jsonpickle
import hashlib

app = Flask(__name__)
app.config.from_object('app_config')
client = MongoClient(app.config["MONGO_URI"])
db = client["admin"]
s3 = boto3.resource(
    service_name='s3',
    region_name=app.config["AWS_REGION"],
    aws_access_key_id=app.config["AWS_ACCESSID"],
    aws_secret_access_key= app.config["AWS_ACCESSKEY"]
)

class ImageStatus(Enum):
    RUNNING = 1
    CANCELED = 2
    COMPLETE = 3

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
        if request.authorization.username == "":
            raise BadRequest('Username must not be null')
        if request.authorization.password == "":
            raise BadRequest('Password must not be null')
        user = db.users.find_one({ "username":  request.authorization.username })
        if user is None:
            raise BadRequest('No user associated with the provided username')
        if user["password"] != request.authorization.password:
            raise BadRequest('Password is incorrect')
        return f(*args, **kwargs)
    return decorated_function


#recieves base64 image data, uploads it to the filesystem and pushes the task to the workers
@app.route('/image/upload', methods=['POST'])
@authenticate
def image_upload():
    img_data = str(request.data).split(',')[-1]
    now = datetime.now()
    hash_str = hashlib.sha224((now.strftime("%m/%d/%Y, %H:%M:%S") + request.authorization.username).encode('utf-8')).hexdigest() #hash by ms as two requests could be sent in a sec
    #check against mongo to see if hash exists, recreate hash if it does. if not create entry "not done" if its not done
    while not db.images.find_one({ "id":  hash_str }) is None:
        hash_str = hashlib.sha224((now.strftime("%m/%d/%Y, %H:%M:%S") + request.authorization.username).encode('utf-8')).hexdigest()
    db.images.insert_one({ "id": hash_str, "username": request.authorization.username, 
    "timeCreated": now.strftime("%m/%d/%Y, %H:%M:%S"), "status": ImageStatus.RUNNING.value, "fakeChance": 0 })

    #write image to filesystem
    new_image_name = hash_str + ".jpg"
    with open(app.config["BASE_IMAGE_PATH"] + new_image_name, "wb") as image_result:
        image_decode = base64.b64decode(img_data)
        image_result.write(image_decode)
        s3.Bucket(app.config["AWS_S3_BUCKET"]).upload_file(Filename=app.config["BASE_IMAGE_PATH"] + new_image_name, Key=new_image_name)

    connection = pika.BlockingConnection(pika.ConnectionParameters(app.config["MQ_HOST"]))
    channel = connection.channel()
    #push image hash to round robin task queue for processing
    channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=hash_str)
    connection.close()

    response_pickled = jsonpickle.encode({"imageId": hash_str})
    return Response(response=response_pickled, status=200, mimetype="application/json")


#gets the result of the processes image by id
@app.route('/image/result', methods=['GET'])
@authenticate
def image_result():
    if request.args.get('imageId') == "" or request.args.get('imageId') == None:
        raise BadRequest('imageId must be supplied in the request')
    image = db.images.find_one({"id":  request.args.get('imageId')})
    if image == None:
        raise BadRequest('The supplied imageId ' + request.args.get('imageId') + ' could not be found')
    

    image_status = ImageStatus(int(image["status"]))
    response_message = ""

    if image_status == ImageStatus.RUNNING:
        return Response(response="Image is still being processed", status=200, mimetype="application/json")
    if image_status == ImageStatus.CANCELED:
        return Response(response="Failed to process image, please re-upload to try again", status=200, mimetype="application/json")
    else:
        response_pickled = jsonpickle.encode({"fakeChance": image["fakeChance"]})
        return Response(response=response_pickled, status=200, mimetype="application/json")


#creates a user with username and password supplied
@app.route('/users/create', methods=['POST'])
def users_create():
    data = request.get_json()
    if not "username" in data or data["username"] == "":
        raise BadRequest('A username must be provided')
    if not "password" in data or data["password"] == "":
        raise BadRequest('A password must be provided')
    if not db.users.find_one({ "username":  data["username"] }) is None:
        raise BadRequest('Username provided already exists')
    db.users.insert_one({"username": data["username"], "password": data["password"]})
    return Response(status=200, mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)