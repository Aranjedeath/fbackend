import os
import urls
from app import app

TEMP_DIR = '/tmp/request'
if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)

if __name__ == '__main__':
    print app.url_map
    app.run('127.0.0.1', 8000)
