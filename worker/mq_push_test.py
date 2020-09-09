import sys
import pika
from worker_config_dev import config_dev
#match app_config.py below
config = config_dev
connection = pika.BlockingConnection(pika.ConnectionParameters(config["MQ_HOST"]))
channel = connection.channel()

channel.basic_publish(exchange='',
                routing_key='task_queue',
                body=sys.argv[1])
connection.close()