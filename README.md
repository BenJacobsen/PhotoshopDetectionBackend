# PhotoshopDetectionBackend

This repo contains the pieces for a distributed image processing backend accessible through a Flask Web API. 

The intended purpose is to detect images of photoshopped faces using the lovely model from https://github.com/PeterWang512/FALdetector , but the processing aspect is quite modular.

This app forces users to register, and needs image data to be base64 encoded. After an image is uploaded, an ID will be returned that can be used to lookup the results of the image's processing. The endpoints can be understood by looking into the postman tests.

The Web API will publish the image ID to a RabbitMQ on uploads which will then use the ID to lookup the image on a shared filesystem which will be distributed to workers in a round robin fashion. User and image info will be stored with MongoDB which the Web API and workers need access to. The shared filesystem is currently implemented by an AWS S3 bucket.

# Configuration

1. Configure MongoDB, a RabbitMQ server, and an AWS S3 bucket to be shared by every machine.

2. Follow the instructions based on the role the machine is filling.

Web API (app.py):

3. Install python 3.x and pip3.

4. ../PhotoshopDetectionBackend/ $ pip3 install -r requirements.txt

5. Set environment variables in app_config.py

6.  ../PhotoshopDetectionBackend/ $ py app.py

Workers (worker/worker.py): 

3. Install python 3.x and pip3.

4. ../PhotoshopDetectionBackend/worker/ $ pip3 install -r requirements.txt

5. Set environment variables in worker_config.py

6. ../PhotoshopDetectionBackend/worker/ $ py worker.py
