import json
from typing import Union
import datetime


class Responser:
    def __init__(self):
        self.errors = []
        self.request = None

    def json_response(self, keys: list, data: Union[list, tuple]):
        """
        Generates json with request, errors info and response - assigned data to keys
        :param keys: key names
        :param data: data to assign with keys
        :return: json prepared response
        """
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
                    pre_json[keys[key_i]] = data[key_i].strftime("%d.%m.%y %H:%M")
                else:
                    pre_json[keys[key_i]] = data[key_i]
        to_dump["response"] = pre_json
        to_dump["errors"] = self.errors
        response = json.dumps(to_dump)
        self.flush()
        return response

    def simple_response(self, success=True):
        """
        Generates simple response with success status, request and errors info
        :param success:
        :return: json prepared simple response
        """
        to_dump = dict()
        to_dump["request"] = self.request
        to_dump["response"] = {"success": success}
        to_dump["errors"] = self.errors
        response = json.dumps(to_dump)
        self.flush()
        return response

    def id_not_found_error(self, raw_error=None):
        """
        Generates error response with error of absence of requested id
        :param raw_error: optional - raw exception
        :return: json prepared simple response with id not found error
        """
        self.errors += [{"error_id": -1, "error_description": "id not found"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def communication_error(self, raw_error=None):
        """
        Generates error response with error of database communication
        :param raw_error: optional - raw exception
        :return: json prepared simple response with database communication error
        """
        self.errors += [{"error_id": -2, "error_description": "database communication issue"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def connection_error(self, raw_error=None):
        """
        Generates error response with error of database connection
        :param raw_error: optional - raw exception
        :return: json prepared simple response with database connection error
        """
        self.errors += [{"error_id": -3, "error_description": "database connection issue"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def empty_request(self, raw_error=None):
        """
        Generates error response with error of empty request
        :return: json prepared simple response with database empty request error
        """
        self.errors += [{"error_id": -4, "error_description": "empty request"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def bad_request(self, raw_error=None):
        """
        Generates error response with error of wrong request
        :return: json prepared simple response with database bad request error
        """
        self.errors += [{"error_id": -5, "error_description": "bad request"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def unauthorized_request(self, raw_error=None):
        """
        Generates error response with error of unauthorized request
        :return: json prepared simple response with database unauthorized request error
        """
        self.errors += [{"error_id": -6, "error_description": "unauthorized request"}]
        if raw_error is not None:
            self.errors[-1]["raw_error"] = raw_error
        return self.json_error()

    def json_error(self):
        """
        Generates error response with request and response and errors info from the class
        :return: json prepared simple response with database connection error
        """
        to_dump = dict()
        to_dump["request"] = self.request
        to_dump["response"] = {"success": False}
        to_dump["errors"] = self.errors
        response = json.dumps(to_dump)
        self.flush()
        return response

    def flush(self):
        """
        Reset errors and request values
        """
        self.errors = []
        self.request = None
