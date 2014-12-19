import urls

from app import app

if __name__ == '__main__':
    print app.url_map
    app.run('127.0.0.1', 8000)
