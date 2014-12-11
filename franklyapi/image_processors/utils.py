import requests
import uuid

def download_file(url):
    res = requests.get(url)
    path= '/tmp/downloads/%s'%(uuid.uuid4().hex)
    if res.status_code == 200:
        with open(path, 'wb') as f:
            f.write(res.content)
        return path