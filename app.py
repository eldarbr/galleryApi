from flask import Flask
from flask import request
from db import Databaser
from responses import Responser
from auth import Authorizer

responser = Responser()
database = Databaser()
authorizer = Authorizer()
app = Flask(__name__)


@app.route('/master/<task>/<subject>')
def serve_master(task, subject):
    headers = request.headers
    if "Authorization" in headers:
        if authorizer.authorize(headers["Authorization"]):
            """
            IMPLEMENTATION OF MASTER REQUESTS SERVING
            """
            pass
    return responser.unauthorized_request()


@app.route('/client/<task>')
def serve_client(task):
    try:
        _id = request.args['id']
    except KeyError:
        _id = None
    if task == "photo":
        if _id is None:
            return responser.empty_request()
        return database.get_photo_by_id(_id)
    elif task == "category":
        if _id is None:
            return responser.empty_request()
        return database.get_category_by_id(_id)
    elif task == "photos_in_category":
        if _id is None:
            return responser.empty_request()
        return database.get_photos_by_category(_id)
    elif task == "categories_of_photo":
        if _id is None:
            return responser.empty_request()
        return database.get_categories_by_photo(_id)
    elif task == "index":
        return database.get_gallery_index()
    elif task == "categories_index":
        return database.get_gallery_index(True)
    else:
        return responser.wrong_request()


if __name__ == '__main__':
    app.run()
