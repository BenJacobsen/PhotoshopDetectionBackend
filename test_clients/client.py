import requests
import json
import subprocess
addr = 'http://localhost:5000'
test_url = addr + '/api/test'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}
img_path = 'C:/Projects/FALdetector-master/examples/modified.jpg'
img = open(img_path, 'rb').read()

response = requests.post(test_url, data=img, headers=headers)
# decode response
print(json.loads(response.text))