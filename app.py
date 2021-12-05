# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from db import Databaser
from responses import Responser
from auth import Authorizer
from config import Configurator

responser = Responser()
database = Databaser()
authorizer = Authorizer()
app = Flask(__name__)


# Master requests
@app.route('/master/<task>/<subject>', methods=['POST'])
@app.route('/master/<task>/<subject>/<infra_subject>', methods=['POST'])
def serve_master(task, subject, infra_subject=None):
    headers = request.headers
    if "Authorization" in headers:
        if authorizer.authorize(headers["Authorization"]):

            if subject == "photo":
                if task in ("insert", "modify"):
                    _description = request.form.get("description", default=None)
                    _timestamp = request.form.get("timestamp", default=None)
                    _hidden = request.form.get("hidden", default=None)

                    # insert photo
                    if task == "insert":
                        try:
                            _name = request.form['name']
                        except KeyError:
                            return bad_request("")
                        return database.insert_photo(_name, _description, _timestamp, _hidden)

                    # modify photo
                    elif task == "modify":
                        try:
                            _id = request.form['id']
                        except KeyError:
                            return bad_request("")
                        _name = request.form.get('name', default=None)
                        return database.modify_photo(_id, _name, _description, _timestamp, _hidden)

                # get photo by id
                elif task == "get":
                    try:
                        _id = request.form['id']
                    except KeyError:
                        return bad_request("")
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    _incomplete = bool(request.form.get('include_incomplete', default=False))
                    return database.get_photo_by_id(_id, _hidden, _incomplete)

                # get photos index
                elif task == "index":
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    _incomplete = bool(request.form.get('include_incomplete', default=False))
                    return database.get_gallery_index(return_hidden=_hidden, return_incomplete=_incomplete)

            elif subject == "category":
                if task in ("insert", "modify"):
                    _description = request.form.get("description", default=None)
                    _hidden = bool(request.form.get("hidden", default=False))

                    # insert category
                    if task == "insert":
                        try:
                            _name = request.form["name"]
                            _alias = request.form["alias"]
                        except KeyError:
                            return bad_request("")
                        return database.insert_category(_name, _alias, _description, _hidden)

                    # modify category
                    elif task == "modify":
                        try:
                            _id = request.form["id"]
                        except KeyError:
                            return bad_request("")
                        _name = request.form.get("name")
                        _alias = request.form.get("alias")
                        return database.modify_category(_id, _name, _alias, _description, _hidden)

                # get category by label
                elif task == "get":
                    try:
                        _id = request.form['label']
                    except KeyError:
                        return bad_request("")
                    _hidden = bool(request.form.get('include_hidden', default=False))
                    return database.get_category_by_label(_id, _hidden)

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
                    if task == "add":
                        return database.assign_photo_to_categories(_photo_id, _category_ids_list)
                    elif task == "replace":
                        return database.modify_photo_to_categories(_photo_id, _category_ids_list)
                    elif task == "delete":
                        return database.delete_photo_to_categories(_photo_id)
                    elif task == "get":
                        return database.get_categories_by_photo(_photo_id, _hidden)

                elif infra_subject == "category" and _category_id is not None:
                    if task == "add":
                        return database.assign_category_to_photos(_category_id, _photo_ids_list)
                    elif task == "replace":
                        return database.modify_category_to_photos(_category_id, _photo_ids_list)
                    elif task == "delete":
                        return database.delete_category_to_photos(_category_id)
                    elif task == "get":
                        return database.get_photos_by_category(_category_id, _hidden)

            # modify yandex api configuration
            elif subject == "config":
                if task == "modify":
                    config = Configurator()
                    _token = request.form.get("yadisk_token", default=None)
                    _folder = request.form.get("yadisk_folder", default=None)
                    config.yadisk_api_rewrite(_token, _folder)
                    return responser.simple_response()

            return not_found("")

    return unauthorized("")


# Client requests
@app.route('/client/<task>', methods=['GET'])
def serve_client(task):
    _id = request.args.get('id', None)
    _label = request.args.get('label', None)
    if task == "photo":
        if _id is None:
            return bad_request("")
        return database.get_photo_by_id(_id)
    elif task == "category":
        if _label is None:
            return bad_request("")
        return database.get_category_by_label(_label)
    elif task == "photos_of_category":
        if _label is None:
            return bad_request("")
        _id = database.get_category_id_by_label(_label)
        return database.get_photos_by_category(_id)
    elif task == "categories_of_photo":
        if _id is None:
            return bad_request("")
        return database.get_categories_by_photo(_id)
    elif task == "index":
        return database.get_gallery_index()
    elif task == "categories_index":
        return database.get_gallery_index(categories=True)
    else:
        return not_found("")


@app.errorhandler(400)
def bad_request(e):
    return responser.bad_request(), 400


@app.errorhandler(401)
def unauthorized(e):
    return responser.unauthorized_request(), 401


@app.errorhandler(404)
def not_found(e):
    return responser.not_found(), 404


@app.errorhandler(405)
def not_found(e):
    return responser.unallowed_method(), 405


if __name__ == '__main__':
    app.run()
