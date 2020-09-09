#!/usr/bin/env python
import pika, sys, os, re, subprocess
import boto3
from pymongo import MongoClient
from enum import Enum
from worker_config import config
#match app_config.py below

class ImageStatus(Enum):
    RUNNING = 1
    CANCELED = 2
    COMPLETE = 3

client = MongoClient(config["MONGO_URI"])
db = client["admin"]
s3 = boto3.resource(
    service_name='s3',
    region_name=config["AWS_REGION"],
    aws_access_key_id=config["AWS_ACCESSID"],
    aws_secret_access_key= config["AWS_ACCESSKEY"]
)

#normally configured to use https://github.com/PeterWang512/FALdetector for processing. Use test_process.py as a placeholder first
def construct_call_str(img_name):
    #return 'python ' + config["IMG_PROCESS_PATH"] + 'global_classifier.py --model_path ' + config["IMG_PROCESS_PATH"] 
    #+  r'weights\global.pth --input_path ' + config["BASE_IMAGE_PATH"] + img_name + ".jpg"
    return 'python ' + config["THIS_DIR"] + 'test_process.py'

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue')

    def callback(ch, method, properties, body):

        print(" [x] Received %r" % body)
        img_hash = body.decode("utf-8")
        img_name = img_hash + ".jpg"
        s3.Bucket(config["AWS_S3_BUCKET"]).download_file(Key=img_name, Filename=config["BASE_IMAGE_PATH"] + img_name)
        proc = subprocess.Popen(args=construct_call_str(body).split(), stdout=subprocess.PIPE, cwd=config["IMG_PROCESS_PATH"])
        proc.wait()
        #if no errors set the image document to COMPLETE with the outputted fakeChance
        if proc.returncode == 0:
            stdout = proc.stdout.read().decode('utf-8')
            fake_chance = int(re.findall(r'[0-9]+', stdout)[0])
            db.images.update_one({"id": img_hash}, { "$set": {"status": ImageStatus.COMPLETE.value, "fakeChance": fake_chance } })
        #if there are errors set the image document to CANCELED
        else:
            db.images.update_one({"id": img_name}, { "$set": {"status": ImageStatus.CANCELED.value } })

    channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)