from flask import Flask
from flask import request
from db import Databaser
from responses import Responser
from auth import Authorizer

responser = Responser()
database = Databaser()
authorizer = Authorizer()
app = Flask(__name__)


@app.route('/master/<task>/<subject>', methods=['POST'])
@app.route('/master/<task>/<subject>/<infra_subject>', methods=['POST'])
def serve_master(task, subject, infra_subject=None):
    headers = request.headers
    if "Authorization" in headers:
        if authorizer.authorize(headers["Authorization"]):

            if subject == "photo":
                if task in ("create", "modify"):
                    _description = request.form.get("description", default=None)
                    _timestamp = request.form.get("timestamp", default=None)
                    _hidden = bool(request.form.get("hidden", default=False))
                    _categories = request.form.get("categories", default=None)  # list of categories
                    if task == "create":
                        try:
                            _name = request.form['name']
                            _href = request.form['href']
                        except KeyError:
                            return responser.bad_request()
                        return database.insert_photo(_href, _name, _description, _timestamp, _hidden, _categories)
                    elif task == "modify":
                        try:
                            _id = request.form['id']
                        except KeyError:
                            return responser.bad_request()
                        _name = request.form.get('name', default=None)
                        _href = request.form.get('href', default=None)
                        return database.modify_photo(_id, _href, _name, _description, _timestamp, _hidden, _categories)

            elif subject == "category":
                if task in ("create", "modify"):
                    _description = request.form.get("description", default=None)
                    _hidden = bool(request.form.get("hidden", default=False))
                    _photos = request.form.get("photos", default=None)  # list of photos
                    if task == "create":
                        try:
                            _name = request.form["name"]
                        except KeyError:
                            return responser.bad_request()
                        return database.insert_category(_name, _description, _hidden, _photos)
                    elif task == "modify":
                        try:
                            _id = request.form["id"]
                        except KeyError:
                            return responser.bad_request()
                        _name = request.form.get("name")
                        return database.modify_category(_id, _name, _description, _hidden, _photos)

            elif subject == "relation":
                if infra_subject is None:
                    return responser.bad_request()

                _photo_id = request.form.get("photo_id", default=None)
                _category_id = request.form.get("category_id", default=None)
                one_of_id = bool(_photo_id) ^ bool(_category_id)

                if task in ("create", "modify"):
                    _photos_id_list = request.form.get("photos_id_list", default=None)
                    _categories_id_list = request.form.get("categories_id_list", default=None)

                    one_of_lists = bool(_photos_id_list) ^ bool(_categories_id_list)
                    types_correspondence = bool(_photo_id) ^ bool(_photos_id_list)

                    if one_of_id and one_of_lists and types_correspondence:
                        if infra_subject == "category":
                            if task == "create":
                                return database.assign_category_to_photos(_category_id, _photos_id_list)
                            elif task == "modify":
                                return database.modify_category_to_photos(_category_id, _photos_id_list)
                        elif infra_subject == "photo":
                            if task == "create":
                                return database.assign_photo_to_categories(_photo_id, _categories_id_list)
                            elif task == "modify":
                                return database.modify_photo_to_categories(_photo_id, _categories_id_list)

                elif task in ("delete",):
                    if one_of_id:
                        if infra_subject == "category":
                            if task == "delete":
                                return database.delete_category_to_photos(_category_id)
                        elif infra_subject == "photo":
                            if task == "delete":
                                return database.delete_photo_to_categories(_photo_id)

            return responser.bad_request()
    return responser.unauthorized_request()


@app.route('/client/<task>', methods=['GET'])
def serve_client(task):
    _id = request.args.get('id', None)
    if task == "photo":
        if _id is None:
            return responser.empty_request()
        return database.get_photo_by_id(_id)
    elif task == "category":
        if _id is None:
            return responser.empty_request()
        return database.get_category_by_id(_id)
    elif task == "photos_of_category":
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
        return database.get_gallery_index(categories=True)
    else:
        return responser.bad_request()


if __name__ == '__main__':
    app.run()
