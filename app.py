from flask import Flask

app = Flask(__name__)


@app.route('/get/')
def get_info():
    return 'Hello World!'


@app.route('/add/')
def add_image():
    return "200000"


@app.route('/modify/')
def modify_image():
    return "333333"


if __name__ == '__main__':
    app.run()
