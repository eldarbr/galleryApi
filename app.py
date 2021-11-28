# -*- coding: utf-8 -*-
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
                    _hidden = request.form.get("hidden", default=None)
                    _categories = request.form.getlist("categories")  # list of categories

                    # create photo
                    if task == "create":
                        try:
                            _name = request.form['name']
                            _href_preview = request.form['href_preview']
                            _href_medium = request.form['href_medium']
                            _href_large = request.form['href_large']
                        except KeyError:
                            return responser.bad_request()
                        return database.insert_photo(_name, _href_preview, _href_medium, _href_large, _description,
                                                     _timestamp, _hidden, _categories)

                    # modify photo
                    elif task == "modify":
                        try:
                            _id = request.form['id']
                        except KeyError:
                            return responser.bad_request()
                        _name = request.form.get('name', default=None)
                        _href_preview = request.form.get('href_preview', default=None)
                        _href_medium = request.form.get('href_medium', default=None)
                        _href_large = request.form.get('href_large', default=None)
                        return database.modify_photo(_id, _name, _href_preview, _href_medium, _href_large, _description,
                                                     _timestamp, _hidden, _categories)

                # get photo by id
                elif task == "get":
                    try:
                        _id = request.form['id']
                    except KeyError:
                        return responser.bad_request()
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    return database.get_photo_by_id(_id, _hidden)

                # get photos index
                elif task == "index":
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    return database.get_gallery_index(return_hidden=_hidden)

            elif subject == "category":
                if task in ("create", "modify"):
                    _description = request.form.get("description", default=None)
                    _hidden = bool(request.form.get("hidden", default=False))
                    _photos = request.form.getlist("photos")  # list of photos

                    # create category
                    if task == "create":
                        try:
                            _name = request.form["name"]
                            _alias = request.form["alias"]
                        except KeyError:
                            return responser.bad_request()
                        return database.insert_category(_name, _alias, _description, _hidden, _photos)

                    # modify category
                    elif task == "modify":
                        try:
                            _id = request.form["id"]
                        except KeyError:
                            return responser.bad_request()
                        _name = request.form.get("name")
                        _alias = request.form.get("alias")
                        return database.modify_category(_id, _name, _alias, _description, _hidden, _photos)

                # get category by id
                elif task == "get":
                    try:
                        _id = request.form['id']
                    except KeyError:
                        return responser.bad_request()
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    return database.get_category_by_id(_id, _hidden)

                # get categories index
                elif task == "index":
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    return database.get_gallery_index(categories=True, return_hidden=_hidden)

            # work with relations between categories and photos
            elif subject == "relation":
                _photo_id = request.form.get("photo_id", default=None)
                _category_id = request.form.get("category_id", default=None)
                _photo_ids_list = request.form.getlist("photo_ids_list")
                _category_ids_list = request.form.getlist("category_ids_list")
                _hidden = bool(request.form.get('include_hidden', default=False))

                if infra_subject == "photo" and _photo_id is not None:
                    if task == "create":
                        return database.assign_photo_to_categories(_photo_id, _category_ids_list)
                    elif task == "modify":
                        return database.modify_photo_to_categories(_photo_id, _category_ids_list)
                    elif task == "delete":
                        return database.delete_photo_to_categories(_photo_id)
                    elif task == "get":
                        return database.get_categories_by_photo(_photo_id, _hidden)

                elif infra_subject == "category" and _category_id is not None:
                    if task == "create":
                        return database.assign_category_to_photos(_category_id, _photo_ids_list)
                    elif task == "modify":
                        return database.modify_category_to_photos(_category_id, _photo_ids_list)
                    elif task == "delete":
                        return database.delete_category_to_photos(_category_id)
                    elif task == "get":
                        return database.get_photos_by_category(_category_id, _hidden)

                return responser.bad_request()

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
