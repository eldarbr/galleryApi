from flask import Flask
from flask import request
import db
from responses import Responser

responser = Responser()
database = db.Databaser()
app = Flask(__name__)


@app.route('/master/<task>')
def serve_master(task):
    pass


@app.route('/client/<task>')
def serve_client(task):
    try:
        _id = request.args['id']
    except KeyError:
        return responser.empty_request()
    if task == "photo":
        return database.get_photo_by_id(_id)
    elif task == "category":
        return database.get_category_by_id(_id)
    elif task == "photos_in_category":
        return database.get_photos_by_category(_id)
    elif task == "categories_of_photo":
        return database.get_categories_by_photo(_id)
    else:
        return responser.empty_request()


if __name__ == '__main__':
    app.run()
