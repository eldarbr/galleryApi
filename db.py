import psycopg2
import json
from config import Configurator
from responses import Responser


class Databaser:
    def __init__(self):
        try:
            config = Configurator()
            self.connection = psycopg2.connect(config.database())
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)
            self.connection = None

    def insert_photo(self, photo_name, href_preview, href_medium, href_large,
                     photo_description=None, timestamp=None, hidden=False, photo_categories=None):
        """
        Inserts photo to database
        :param photo_name: name of photo
        :param href_preview: link to CDN
        :param href_medium: link to CDN
        :param href_large: link to CDN
        :param photo_description: description of photo
        :param timestamp: when photo was taken
        :param hidden: if the photo is hidden; default-False
        :param photo_categories: list of categories that should be assigned
        :return: json with inserted photo id in response tag, errors in errors tag
        """
        responser = Responser()
        responser.request = {"photo_name": photo_name, "expected": "insertion"}
        if not self.check_connection():
            return responser.connection_error()
        if photo_categories is None:
            photo_categories = []
        cursor = self.cursor
        try:
            cursor.execute("""INSERT
                           INTO photos (name, description, date_taken, hidden, href_preview, href_medium, href_large)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           RETURNING photo_id""",
                           (photo_name, photo_description, timestamp, bool(hidden), href_preview, href_medium,
                            href_large))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        photo_id = cursor.fetchall()[0][0]

        assign_categories = self.assign_photo_to_categories(photo_id, photo_categories)
        responser.errors += json.loads(assign_categories)["errors"]
        return responser.json_response(["photo_id"], (photo_id,))

    def modify_photo(self, photo_id, photo_name=None, href_preview=None, href_medium=None, href_large=None,
                     photo_description=None, timestamp=None, hidden=None, photo_categories=None):
        """
        Replaces entry at photos table with specified data maintaining photo id
        Re-assigns categories (initiates photos_categories table modify)
        :param photo_id: id of photo to be modified
        :param photo_name: name of photo
        :param href_preview: link to CDN
        :param href_medium: link to CDN
        :param href_large: link to CDN
        :param photo_description: description of photo
        :param timestamp: when photo was taken
        :param hidden: if the photo is hidden; default-False
        :param photo_categories: list of categories that should be assigned
        :return: json with errors and success status
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "modification"}
        if not self.check_connection():
            return responser.connection_error()
        new_values = (photo_name, photo_description, timestamp, hidden, href_preview, href_medium, href_large)
        try:
            cursor.execute("SELECT * FROM photos WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        if len(cursor.fetchall()) == 0:
            return responser.id_not_found_error()
        else:
            columns = self.current_columns_names()[1:]
            changed_columns = []
            for key in range(len(new_values)):
                if new_values[key] is not None:
                    changed_columns += [columns[key] + "=%s"]
            if len(changed_columns) == 0:
                return responser.bad_request("nothing has changed")
            changed_columns = ", ".join(changed_columns)
            values = tuple([x for x in new_values if x is not None])
            try:
                cursor.execute("""UPDATE photos SET {}
                               WHERE photo_id=%s""".format(changed_columns), values + (photo_id,))
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print(e)
                return responser.communication_error(str(e))
        if photo_categories is not None:
            return self.modify_photo_to_categories(photo_id, photo_categories)
        else:
            return responser.simple_response()

    def assign_photo_to_categories(self, photo_id, category_ids):
        """
        Creates assignment of the photo id with the category ids
        :return: json with errors and success status
        """
        print("Create photo to categories relation")
        print(photo_id, " | ", category_ids)
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "categories assignment"}
        if not self.check_connection():
            return responser.connection_error()
        if len(category_ids) > 0:
            for category_id in category_ids:
                print("try creating relation", photo_id, category_id)
                responser.errors += self.assign_photo_category(photo_id, category_id)
        return responser.simple_response()

    def modify_photo_to_categories(self, photo_id, category_ids):
        """
        Re-assigns the photo id with the category ids
        by deleting previous assignation and adding new one
        :return: json with errors and success status
        """
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "categories re-assignment"}
        if not self.check_connection():
            return responser.connection_error()
        delete = self.delete_photo_to_categories(photo_id)
        if "success" in json.loads(delete)["response"]:
            return self.assign_photo_to_categories(photo_id, category_ids)
        else:
            return delete

    def delete_photo_to_categories(self, photo_id):
        """
        Deletes assignation with any category
        :return: json with errors and success status
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "categories un-assignment"}
        if not self.check_connection():
            return responser.connection_error()
        try:
            cursor.execute("DELETE FROM photos_categories WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            responser.communication_error(str(e))
        return responser.simple_response()

    def insert_category(self, category_name, alias, category_description=None, hidden=False, category_photos=None):
        """
        Inserts category to database
        :param category_name: name of category
        :param alias: text alias for category
        :param category_description: description of category
        :param hidden: if the category should be hidden
        :param category_photos: list of photos to assign with this category
        :return: json with errors and new category id
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"category_name": category_name, "expected": "insertion"}
        if not self.check_connection():
            return responser.connection_error()
        if category_photos is None:
            category_photos = []
        try:
            cursor.execute("""INSERT INTO categories (name, description, hidden, alias)
                           VALUES (%s, %s, %s, %s)
                           RETURNING category_id""", (category_name, category_description, hidden, alias))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        category_id = cursor.fetchall()[0][0]
        assign_photos = self.assign_category_to_photos(category_id, category_photos)
        responser.errors += json.loads(assign_photos)["errors"]
        return responser.json_response(["category_id"], (category_id,))

    def modify_category(self, category_id, category_name=None, alias=None, category_description=None,
                        hidden=None, category_photos=None):
        """
        Modify category info by id. Replace old data with new data.
        :param category_id: id of category to modify
        :param category_name: optional - new name
        :param alias: new text alias for the category
        :param category_description: optional - new description
        :param hidden: optional - new hidden status
        :param category_photos: optional - new list of photos to assign with this category
        :return: json with errors and success status
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "modification"}
        if not self.check_connection():
            return responser.connection_error()
        new_values = (category_name, category_description, hidden, alias)
        try:
            cursor.execute("SELECT * FROM category WHERE photo_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        if len(cursor.fetchall()) == 0:
            return responser.id_not_found_error()
        else:
            columns = self.current_columns_names()[1:]
            changed_columns = []
            for key in range(len(new_values)):
                if new_values[key] is not None:
                    changed_columns += [columns[key] + "=%s"]
            if len(changed_columns) == 0:
                return responser.bad_request("nothing has changed")
            changed_columns = ", ".join(changed_columns)
            values = tuple([x for x in new_values if x is not None])
            try:
                cursor.execute("""UPDATE category SET {}
                               WHERE category_id=%s""".format(changed_columns), values + (category_id,))
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print(e)
                return responser.communication_error(str(e))
        if category_photos is not None:
            return self.modify_photo_to_categories(category_id, category_photos)
        return responser.simple_response()

    def assign_category_to_photos(self, category_id, photo_ids):
        """
        Creates assignment of the photo id with the category ids
        :return: json with errors and success status
        """
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "photos assignment"}
        if not self.check_connection():
            return responser.connection_error()
        if len(photo_ids) > 0:
            for photo_id in photo_ids:
                responser.errors += self.assign_photo_category(photo_id, category_id)
        return responser.simple_response()

    def modify_category_to_photos(self, category_id, photo_ids):
        """
        Re-assigns photos with specified category
        :param category_id: target category
        :param photo_ids: list of photos to assign with this category
        :return: json with errors and success status
        """
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "photos re-assignment"}
        if not self.check_connection():
            return responser.connection_error()
        delete = self.delete_category_to_photos(category_id)
        if "success" in json.loads(delete)["response"]:
            return self.assign_category_to_photos(category_id, photo_ids)
        else:
            return delete

    def delete_category_to_photos(self, category_id):
        """
        Deletes all assignment of specified category
        :param category_id: category to unassign
        :return: json with errors and success status
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "photos un-assignment"}
        if not self.check_connection():
            return responser.connection_error()
        try:
            cursor.execute("DELETE FROM photos_categories WHERE category_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        return responser.simple_response()

    def get_photo_by_id(self, photo_id, return_hidden=False):
        """
        Return photo from database by id
        :param photo_id: input photo id
        :param return_hidden: if the method should return hidden photos
        :return: json with data
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "photo by id"}
        if not self.check_connection():
            return responser.connection_error()
        if return_hidden:
            hidden_mark = (True, False)
        else:
            hidden_mark = (False,)
        try:
            cursor.execute("SELECT * FROM photos WHERE photo_id=%s and hidden in %s", (photo_id, hidden_mark))
            self.connection.commit()
        except Exception as e:
            self.connection.commit()
            print(e)
            return responser.communication_error(str(e))
        result = cursor.fetchall()
        if len(result) == 0:
            return responser.id_not_found_error()
        columns = self.current_columns_names()
        return responser.json_response(columns, result[0])

    def get_categories_by_photo(self, photo_id, return_hidden=False):
        """
        Returns categories that are assigned with specified photo id
        :param photo_id:
        :param return_hidden: True If hidden categories are needed too
        :return: json with data and errors
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"photo_id": photo_id, "expected": "categories by photo"}
        if not self.check_connection():
            return responser.connection_error()
        try:
            cursor.execute("SELECT * FROM photos_categories WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        result = cursor.fetchall()
        if len(result) == 0:
            return responser.id_not_found_error()
        raw_categories = [tup[1] for tup in result]
        if return_hidden:
            hidden_mark = (True, False)
        else:
            hidden_mark = (False,)
        try:
            cursor.execute("select * from categories where category_id in %s and hidden in %s",
                           (tuple(raw_categories), hidden_mark))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        columns = self.current_columns_names()
        data = cursor.fetchall()
        return responser.json_response(columns, data)

    def get_category_by_id(self, category_id, return_hidden=False):
        """
        Return category from database by id
        :param category_id: input category id
        :param return_hidden: if the method should return hidden category
        :return: json with data
        """
        cursor = self.cursor
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "category by id"}
        if not self.check_connection():
            return responser.connection_error()
        if return_hidden:
            hidden_mark = (True, False)
        else:
            hidden_mark = (False,)
        try:
            cursor.execute("select * from categories where category_id=%s and hidden in %s",
                           (category_id, hidden_mark))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            responser.communication_error(str(e))
        result = cursor.fetchall()
        if len(result) == 0:
            return responser.id_not_found_error()
        columns = self.current_columns_names()
        return responser.json_response(columns, result[0])

    def get_photos_by_category(self, category_id, return_hidden=False):
        """
        Json-constructed (Responser) array in parent photos
        :param category_id:
        :param return_hidden:
        :return:
        """
        responser = Responser()
        responser.request = {"category_id": category_id, "expected": "photos by category"}
        if not self.check_connection():
            return responser.connection_error()
        cursor = self.cursor
        try:
            cursor.execute("SELECT * FROM photos_categories WHERE category_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))

        result = cursor.fetchall()
        if len(result) == 0:
            return responser.id_not_found_error()

        raw_photos = [tup[0] for tup in result]
        if return_hidden:
            hidden_mark = (True, False)
        else:
            hidden_mark = (False,)
        try:
            cursor.execute("select * from photos where photo_id in %s and hidden in %s",
                           (tuple(raw_photos), hidden_mark))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))

        columns = self.current_columns_names()
        data = cursor.fetchall()
        return responser.json_response(columns, data)

    def get_gallery_index(self, categories=False, return_hidden=False):
        """
        Returns json with all photos that are not hidden
        :return: json response
        """
        responser = Responser()
        if categories:
            responser.request = {"expected": "categories index"}
        else:
            responser.request = {"expected": "photos index"}
        if not self.check_connection():
            return responser.connection_error()
        cursor = self.cursor
        if categories:
            index_type = "categories"
        else:
            index_type = "photos"
        if return_hidden:
            hidden_mark = (True, False)
        else:
            hidden_mark = (False,)
        try:
            cursor.execute("select * from {} where hidden in %s".format(index_type), hidden_mark)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return responser.communication_error(str(e))
        columns = self.current_columns_names()
        index = cursor.fetchall()
        return responser.json_response(columns, index)

    def assign_photo_category(self, photo_id, category_id):
        """
        Creates assignment of specified photo and category
        :param photo_id: photo id
        :param category_id: category id
        :return: json with list of errors
        """
        cursor = self.cursor
        try:
            cursor.execute("INSERT INTO photos_categories VALUES (%s, %s)", (photo_id, category_id))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return [{"error_id": 0, "raw_error": str(e)}]
        return []

    def current_columns_names(self):
        """
        Columns of database request
        :return: list of columns after a database request
        """
        return [desc[0] for desc in self.cursor.description]

    def check_connection(self):
        """
        Checks connection with database
        :return: connection status
        """
        if self.connection is None or self.connection.closed:
            return False
        return True
