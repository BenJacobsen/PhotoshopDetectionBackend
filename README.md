# PhotoshopDetectionBackend

This repo contains the pieces for a distributed image processing backend accessible through a Flask Web API. 

The intended purpose is to detect images of photoshopped faces using the lovely model from https://github.com/PeterWang512/FALdetector , but the processing aspect is quite modular.

This app forces users to register, and needs image data to be base64 encoded. After an image is uploaded, an ID will be returned that can be used to lookup the results of the image's processing. The endpoints can be understood by looking into the postman tests.

The Web API will publish the image ID to a RabbitMQ on uploads which will then use the ID to lookup the image on a shared filesystem which will be distributed to workers in a round robin fashion. User and image info will be stored with MongoDB which the Web API and workers need access to.

Configuration will be set in /app_config.py and /worker/worker.py
