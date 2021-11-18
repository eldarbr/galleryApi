import psycopg2
import config


class Databaser:
    connection = psycopg2.connect(config.database())
    cursor = connection.cursor()

    def insert_photo(self, photo_href, photo_name, photo_description=None, timestamp=None, hidden=False,
                     photo_categories=None):
        """
        Inserts photo to database
        :param photo_href: href to CDN
        :param photo_name: name of photo
        :param photo_description: description of photo
        :param timestamp: when photo was taken
        :param hidden: if the photo is hidden; default-False
        :param photo_categories: list of categories that should be assigned
        :return: -1 if insertion failed; else photo id, number of errors
        """
        to_return = 0
        if photo_categories is None:
            photo_categories = []
        cursor = self.cursor
        try:
            cursor.execute("INSERT INTO photos (name, description, date_taken, hidden, href)"
                           "VALUES (%s, %s, %s, %s, %s)"
                           "RETURNING photo_id", (photo_name, photo_description, timestamp, hidden, photo_href))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("ERROR - conflict while inserting photo {} into photos".format(photo_name))
            print(e)
            return -1,
        photo_id = cursor.fetchall()[0][0]
        to_return += self.assign_photo_photos_categories(photo_id, photo_categories)
        return photo_id, to_return

    def modify_photo(self, photo_id, photo_href=None, photo_name=None, photo_description=None,
                     timestamp=None, hidden=None, photo_categories=None):
        """
        Replaces entry at photos table with specified data maintaining photo id
        Re-assigns categories (initiates photos_categories table modify)
        :param photo_id: id of photo to be modified
        :param photo_href: href to CDN
        :param photo_name: name of photo
        :param photo_description: description of photo
        :param timestamp: when photo was taken
        :param hidden: if the photo is hidden; default-False
        :param photo_categories: list of categories that should be assigned
        :return: -1 - no id entry found; -2 - update error; -3 - check error; number of errors
        """
        cursor = self.cursor
        new_values = (photo_name, photo_description, timestamp, hidden, photo_href)
        try:
            cursor.execute("SELECT * FROM photos WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
        id_control = cursor.fetchall()
        if len(id_control) == 0:
            return -3
        else:
            values = list(id_control[0][1:])
            for key in range(len(values)):
                if new_values[key] is not None:
                    values[key] = new_values[key]
            values = tuple(values)
            try:
                cursor.execute("UPDATE photos SET name=%s, description=%s, date_taken=%s, hidden=%s, href=%s"
                               "WHERE photo_id=%s", values + (photo_id,))
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print("ERROR modifying photo id {}".format(photo_id))
                print(e)
                return -2
        if photo_categories is not None:
            return self.modify_photo_photos_categories(photo_id, photo_categories)
        else:
            return 0

    def assign_photo_photos_categories(self, photo_id, category_ids):
        """
        Creates assignment of the photo id with the category ids
        :return: number of errors
        """
        to_return = 0
        cursor = self.cursor
        if len(category_ids) > 0:
            for category_id in category_ids:
                try:
                    cursor.execute("INSERT INTO photos_categories VALUES (%s, %s)", (photo_id, category_id))
                    self.connection.commit()
                except Exception as e:
                    self.connection.rollback()
                    print("ERROR - conflict while inserting into photos_categories values {} {}".
                          format(photo_id, category_id))
                    print(e)
                    to_return += 1
        return to_return

    def modify_photo_photos_categories(self, photo_id, category_ids):
        """
        Re-assigns the photo id with the category ids
        by deleting previous assignation and adding new one
        :return: -1 - no id to modify entry was found; number of errors
        """
        if self.delete_photo_photos_categories(photo_id) == 0:
            return self.assign_photo_photos_categories(photo_id, category_ids)
        else:
            return -1

    def delete_photo_photos_categories(self, photo_id):
        """
        Deletes assignation with any category
        :return: 0 - ok; 1 - no id entry was found
        """
        cursor = self.cursor
        try:
            cursor.execute("DELETE FROM photos_categories WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return 1
        return 0

    def insert_category(self, category_name, category_description=None, hidden=False, category_photos=None):
        cursor = self.cursor
        if category_photos is None:
            category_photos = []
        to_return = 0
        try:
            cursor.execute("INSERT INTO categories (name, description, hidden)"
                           "VALUES (%s, %s, %s)"
                           "RETURNING category_id", (category_name, category_description, hidden))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print("ERROR - conflict while inserting category {} into categories".format(category_name))
            print(e)
            return -1,
        category_id = cursor.fetchall()[0][0]
        to_return += self.assign_category_photos_categories(category_id, category_photos)
        return category_id, to_return

    def modify_category(self, category_id, category_name=None, category_description=None,
                        hidden=None, category_photos=None):
        """
        Modify category info by id. Replace old data with optional new
        :param category_id:
        :param category_name:
        :param category_description:
        :param hidden:
        :param category_photos:
        :return:
        """
        cursor = self.cursor
        new_values = (category_name, category_description, hidden)
        try:
            cursor.execute("SELECT * FROM category WHERE photo_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
        id_control = cursor.fetchall()
        if len(id_control) == 0:
            return -1
        else:
            values = id_control[0]
            for key in range(len(values)):
                if new_values[key] is not None:
                    values[key] = new_values[key]
            try:
                cursor.execute("UPDATE category SET name=%s, description=%s, hidden=%s"
                               "WHERE category_id=%s", values + (category_id,))
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print("ERROR modifying photo id {}".format(category_id))
                print(e)
                return -2
        if category_photos is not None:
            return self.modify_photo_photos_categories(category_id, category_photos)

    def assign_category_photos_categories(self, category_id, photo_ids):
        """
        Creates assignment of the photo id with the category ids
        :return: number of errors
        """
        to_return = 0
        cursor = self.cursor
        if len(photo_ids) > 0:
            for photo_id in photo_ids:
                try:
                    cursor.execute("INSERT INTO photos_categories VALUES (%s, %s)", (photo_id, category_id))
                    self.connection.commit()
                except Exception as e:
                    self.connection.rollback()
                    print("ERROR - conflict while inserting values {} {} into photos_categories".
                          format(photo_id, category_id))
                    print(e)
                    to_return += 1
        return to_return

    def modify_category_photos_categories(self, category_id, photo_ids):
        if self.delete_category_photos_categories(category_id) == 0:
            return self.assign_category_photos_categories(category_id, photo_ids)
        else:
            return -1

    def delete_category_photos_categories(self, category_id):
        cursor = self.cursor
        try:
            cursor.execute("DELETE FROM photos_categories WHERE category_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return 1
        return 0

    def get_photo_by_id(self, photo_id):
        """
        Returns tuple
        with data from database - every column - by photo id
        where on place [0] is given photo id
        or 0 if the id entry was not found
        :param photo_id: input photo id
        :return: tuple
        """
        cursor = self.cursor
        try:
            cursor.execute("SELECT * FROM photos WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.commit()
            print(e)
            return -1,
        result = cursor.fetchall()
        if len(result) == 0:
            return 0,
        return result[0]

    def get_categories_by_photo(self, photo_id, need_hidden_categories=False):
        cursor = self.cursor
        try:
            cursor.execute("SELECT * FROM photos_categories WHERE photo_id=%s", [photo_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return [(-1,)]
        result = cursor.fetchall()
        if len(result) == 0:
            return [(0,)]
        raw_categories = [tup[1] for tup in result]
        if need_hidden_categories:
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
            return [(-2,)]
        return cursor.fetchall()

    def get_category_by_id(self, category_id):
        cursor = self.cursor
        try:
            cursor.execute("select * from categories where category_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return -1,
        result = cursor.fetchall()
        if len(result) == 0:
            return 0,
        return result[0]

    def get_photos_by_category(self, category_id, need_hidden_photos=False):
        cursor = self.cursor
        try:
            cursor.execute("SELECT * FROM photos_categories WHERE category_id=%s", [category_id])
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(e)
            return [(-1,)]
        result = cursor.fetchall()
        if len(result) == 0:
            return [(0,)]
        raw_photos = [tup[0] for tup in result]
        if need_hidden_photos:
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
            return [(-2,)]
        return cursor.fetchall()
