from flask import Response
import db
import json
from typing import Union
import datetime
import config


def empty_request():
    return Response('{"error_code":"1001", "message":"Empty request", "status":"400"}', status=400)


class Responser:
    errors = []
    request = None

    def json_response(self, keys: list, data: Union[list, tuple]):
        to_dump = {}
        if self.request is not None:
            to_dump["request"] = self.request
        if type(data) == list:
            pre_json = []
            for unit in data:
                pre_json += [{}]
                for key_i in range(len(keys)):
                    if type(unit[key_i]) == datetime.datetime:
                        pre_json[-1][keys[key_i]] = unit[key_i].strftime("%d.%m.%y %H:%M")
                    else:
                        pre_json[-1][keys[key_i]] = unit[key_i]
        else:
            pre_json = {}
            for key_i in range(len(keys)):
                if type(data[key_i]) == datetime.datetime:
                    data[key_i] = data[key_i].strftime("%d.%m.%y %H:%M")
                pre_json[keys[key_i]] = data[key_i]
        to_dump["response"] = pre_json
        to_dump["errors"] = self.errors
        return json.dumps(to_dump)

    def simple_response(self, success=True):
        to_dump = dict()
        to_dump["request"] = self.request
        to_dump["response"] = {"success": success}
        to_dump["errors"] = self.errors
        return json.dumps(to_dump)

    def id_not_found_error(self, raw_error=None):
        self.errors += [{"error_id": -1, "error_description": "id not found"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def communication_error(self, raw_error=None):
        self.errors += [{"error_id": -2, "error_description": "database communication issue"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def json_error(self):
        to_dump = dict()
        to_dump["request"] = self.request
        to_dump["response"] = {}
        to_dump["errors"] = self.errors
        return json.dumps(to_dump)
