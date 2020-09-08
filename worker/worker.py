#!/usr/bin/env python
import pika, sys, os, re, subprocess
from pymongo import MongoClient
from enum import Enum
#match app_config.py below
config_object = {"BASE_IMAGE_PATH": , "IMG_PROCESS_PATH": ,
"MONGO_URI" : , "MQ_HOST": , "THIS_DIR": }

class ImageStatus(Enum):
    RUNNING = 1
    CANCELED = 2
    COMPLETE = 3

client = MongoClient(config_object["MONGO_URI"])
db = client["admin"]

#normally configured to use https://github.com/PeterWang512/FALdetector for processing. Use test_process.py as a placeholder first
def construct_call_str(img_name):
    #return 'python ' + config_object["IMG_PROCESS_PATH"] + 'global_classifier.py --model_path ' + config_object["IMG_PROCESS_PATH"] 
    #+  r'weights\global.pth --input_path ' + config_object["BASE_IMAGE_PATH"] + img_name + ".jpg"
    return 'python ' + config_object["THIS_DIR"] + 'test_process.py fail'

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue')

    def callback(ch, method, properties, body):

        print(" [x] Received %r" % body)
        img_name = body.decode("utf-8")
        proc = subprocess.Popen(args=construct_call_str(body).split(), stdout=subprocess.PIPE, cwd=config_object["IMG_PROCESS_PATH"])
        proc.wait()
        #if no errors set the image document to COMPLETE with the outputted fakeChance
        if proc.returncode == 0:
            stdout = proc.stdout.read().decode('utf-8')
            fake_chance = int(re.findall(r'[0-9]+', stdout)[0])
            db.images.update_one({"id": img_name}, { "$set": {"status": ImageStatus.COMPLETE.value, "fakeChance": fake_chance } })
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