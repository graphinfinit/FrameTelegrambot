
import os
import sqlite3

# db settings class SqliteDb
DB_NAME = 'telegram.db'
DEFAULT_TABLE_NAME = 'shift_good'
DEFAULT_CONFIG_TABLE = 'config'
DEFAULT_STATE_TABLE = 'states'
DEFAULT_LIMIT_TABLE = 'limittable'

dirname = os.path.dirname(__file__)
DB_PATH = os.path.join(dirname, 'database', '{}'.format(DB_NAME))

class SqliteDb(object):

    def __init__(self, db_path=DB_PATH):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row  #позволяет выводить в виде sqlite3.Row object
        self.cursor = self.connection.cursor()

    # adminpart
    def create_config_table(self, table_name=DEFAULT_CONFIG_TABLE):
        """
        Создает таблицу для хранения названий интервалов для записи
        :param table_name:
        """
        with self.connection:
            try:
                self.cursor.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, shift TEXT)'.format(table_name))
                return True
            except Exception as exc:
                print(exc.args)

    def get_configs(self, table_name=DEFAULT_CONFIG_TABLE):
        with self.connection:
            try:
                return self.cursor.execute('SELECT * FROM {}'.format(table_name)).fetchall()
            except Exception as exc:
                print(exc.args)

    def insert_config(self, shift, table_name=DEFAULT_CONFIG_TABLE):
        with self.connection:
            try:
                self.cursor.execute('INSERT INTO {} (shift) VALUES ("{}") '.format(table_name, shift))
            except Exception as exc:
                print(exc.args)
    def drop_config(self, table_name=DEFAULT_CONFIG_TABLE):
        with self.connection:
            try:
                self.cursor.execute('DROP TABLE {}'.format(table_name))
            except Exception as exc:
                print(exc.args)


    # maxCount
    def set_max(self, limit, table_name=DEFAULT_LIMIT_TABLE):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO {} (vlimit) VALUES ({})".format(table_name, limit))
            except Exception as exc:
                print(exc.args)

    def get_max(self, table_name=DEFAULT_LIMIT_TABLE):
        with self.connection:
            try:
                return self.cursor.execute('SELECT * FROM {}'.format(table_name)).fetchall()
            except Exception as exc:
                print(exc.args)
    def drop_max(self, table_name=DEFAULT_LIMIT_TABLE):
        with self.connection:
            try:
                self.cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
            except Exception as exc:
                print(exc.args)
    def create_limittable(self, table_name=DEFAULT_LIMIT_TABLE):
        with self.connection:
            try:
                self.cursor.execute("CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, vlimit TEXT)".format(table_name))
            except Exception as exc:
                print(exc.args)



    #userspart
    def get(self, user_id, shift, table_name=DEFAULT_TABLE_NAME):
        """ Проверяем есть ли запись  """
        with self.connection:
            try:
                value = self.cursor.execute('SELECT * FROM {} WHERE user_id = "{}" AND shift = "{}"'.format(table_name, user_id, shift)).fetchall()
                if len(value) == 0:
                    return False
                else:
                    return True
            except Exception as exc:
                print(exc.args)

    def select_all(self, table_name=DEFAULT_TABLE_NAME):
        """ Получаем все данные из таблицы записавшихся"""
        with self.connection:
            try:
                return self.cursor.execute('SELECT * FROM {}'.format(table_name)).fetchall()
            except Exception as exc:
                print(exc.args)

    def create_table(self, table_name=DEFAULT_TABLE_NAME):
        """
        Создаем таблицу если она еще не существует с полями
        (ID записи, Дата и время добавления, Номер смены, Id пользователя, user_name)
        :param table_name:
        :return:
        """
        with self.connection:
            try:
                self.cursor.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, shift TEXT, user_id TEXT, user_name TEXT)'.format(table_name))
                return True
            except Exception as exc:
                print(exc.args)

    def insert(self, shift, user_id, user_name, date, table_name=DEFAULT_TABLE_NAME):
        """
        ВСтавляем значения в таблицу !
        :param shift:
        :param user_id:
        :param date:
        :param table_name:
        :return: True
        """
        with self.connection:
            try:
                self.cursor.execute('INSERT INTO {} (date, shift, user_id, user_name) VALUES ("{}", "{}", "{}", "{}") '.format(table_name, date, shift, user_id, user_name))
                return True
            except Exception as exc:
                print(exc.args)

    def delete(self, shift, user_id, table_name=DEFAULT_TABLE_NAME):
        """
        :param shift:
        :param user_id:
        :param table_name:
        :return: True

        """
        with self.connection:
            try:
                self.cursor.execute('DELETE FROM {} WHERE shift = "{}" AND user_id = "{}"'.format(table_name, shift, user_id))
                return True
            except Exception as exc:
                print(exc.args)

    def count_rows(self, shift, table_name=DEFAULT_TABLE_NAME):
        """
        Записавшиеся на определенную смену
        :param shift:
        :param table_name:
        :return:записавшиеся на смену
        """
        with self.connection:
            try:
                result = self.cursor.execute('SELECT * FROM {} WHERE shift = "{}"'.format(table_name, shift)).fetchall()
                return result
            except Exception as exc:
                print(exc.args)
    def drop_table(self):
        """
        Удаление таблицы
        """
        with self.connection:
            try:
                self.cursor.execute('DROP TABLE {}'.format(DEFAULT_TABLE_NAME))
            except Exception as exc:
                print(exc.args)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

"""
    #statepart
    def create_state_table(self, table_name= DEFAULT_STATE_TABLE):
        with self.connection:
            try:
                self.cursor.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY AUTOINCREMENT, state INTEGER)'.format(table_name))
                return True
            except Exception as exc:
                print(exc.args)

    def get_state(self):
        with self.connection:
            try:
                self.cursor.execute('SELECT state FROM {} WHERE id = 1'.format(table_name))
                return True
            except Exception as exc:
                print(exc.args)

    def set_state(self, state):
        with self.connection:
            try:
                self.cursor.execute('UPDATE {} SET state = {} WHERE id = 1'.format(table_name, state))
                return True
            except Exception as exc:
                print(exc.args)

"""