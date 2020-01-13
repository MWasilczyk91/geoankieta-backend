# coding: utf-8

from application import create_app

app = create_app('config.py')
if __name__ == '__main__':
    app.run() #port 5000
