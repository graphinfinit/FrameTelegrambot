"""
@framebot (телеграм бот для записи людей на определенное время)

"""

import telebot
from telebot import types

import time
from datetime import datetime
import sqlite3
import os

from settings import TOKEN, ADMIN_LIST, SHIFTMAX, TIME_END_RECORDS, SHIFT_INTERVALS

# db settings class SqliteDb
DB_NAME = 'telegram.db'
DEFAULT_TABLE_NAME = 'shift_good'

dirname = os.path.dirname(__file__)
DB_PATH = os.path.join(dirname, 'database', '{}'.format(DB_NAME))



bot = telebot.TeleBot(TOKEN, threaded=False)  # отключена многопоточность библиотеки threaded=False
print('Start program...{}'.format(datetime.now()))
class SqliteDb(object):
    def __init__(self, db_path=DB_PATH):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row  #позволяет выводить в виде sqlite3.Row object а не кортежей
        self.cursor = self.connection.cursor()

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
        :return:
        """
        with self.connection:
            try:
                self.cursor.execute('DROP TABLE {}'.format(DEFAULT_TABLE_NAME))
            except Exception as exc:
                print(exc.args)


    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

# Сразу создадим таблицу
initdb = SqliteDb()
initdb.create_table()
initdb.close()

def create_mainkeyboard(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton(text='*записаться')
    itembtn2 = types.KeyboardButton(text='*посмотреть_записи')
    markup.row(itembtn1)
    markup.row(itembtn2)
    bot.send_message(message.chat.id,
                     text='Дамы и господа, я бот для записи',
                     reply_markup=markup)

def create_inlinekeyboarb(message):
    db = SqliteDb()
    inlinekeyboarb = types.InlineKeyboardMarkup(row_width=2)
    for shift in SHIFT_INTERVALS:
        text = SHIFT_INTERVALS[shift]

        if len(db.count_rows(shift=shift)) == SHIFTMAX:
            text = SHIFT_INTERVALS[shift] + " ❌ Запись закрыта"
        itembtn1 = types.InlineKeyboardButton(text=text, callback_data=shift)
        inlinekeyboarb.row(itembtn1)
    db.close()
    bot.send_message(message.chat.id,
                     text='{}, выберите время'.format(message.from_user.first_name),
                     reply_markup=inlinekeyboarb)

def delete_or_insert(call):
    """
    :param call: принимает данные из инлайн-клавиатуры
    :return: answer_callback_query  Делает запрос в БД и показавает всплывающее окно об удаление или добавлении записи
    """
    db = SqliteDb()
    value = db.get(user_id=call.from_user.id, shift=call.data)
    if value == True:
        db.delete(user_id=call.from_user.id, shift=call.data)
        db.close()
        bot.answer_callback_query(callback_query_id=call.id,
                                  show_alert=True,
                                  text="Запись на смену {} удалена".format(SHIFT_INTERVALS[call.data]))
    else:
        if len(db.count_rows(shift=call.data)) == SHIFTMAX:
            db.close()
            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text="{}, записаться уже нельзя. Выберите другую смену!".format(call.from_user.first_name))
        else:
            status = db.insert(shift=call.data, user_id=call.from_user.id, user_name=call.from_user.first_name,
                               date=datetime.now())
            db.close()
            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text="{}, Вы записаны на {}. Нажмите еще раз если хотите отписаться".format(call.from_user.first_name,
                                                                                    SHIFT_INTERVALS[call.data]))

@bot.message_handler(func=lambda m: True)
def process_main(message):
    if message.text == '*записаться':
        create_inlinekeyboarb(message)
    elif message.text == '*посмотреть_записи':
        db = SqliteDb()
        for shift in SHIFT_INTERVALS:
            count_rows = db.count_rows(shift=shift)
            bot.send_message(message.chat.id,
                             text='Записались на {} - {} человек.'.format(SHIFT_INTERVALS[shift], len(count_rows)))

            for row in count_rows:
                row = dict(row)
                text ="<a href='tg://user?id={}'>{}</a>  <i>({})</i> ".format(row['user_id'], row['user_name'], row['date'])

                bot.send_message(message.chat.id, text=text, parse_mode='HTML')
        db.close()
    elif message.text == '/start':
        create_mainkeyboard(message)
    elif message.text == '/drop_db':
        if str(message.from_user.id) in ADMIN_LIST:
            db = SqliteDb()
            db.drop_table()
            db.create_table()
            db.close()
            bot.send_message(message.chat.id, text="<strong>!{}, все записи успешно удалены!</strong>".format(
                message.from_user.first_name), parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, text="<strong>!{}, я слушаюсь только хозяина.</strong>".format(message.from_user.first_name), parse_mode='HTML')

    else:
        pass


@bot.callback_query_handler(func=lambda call: True)
def process_call(call):
    for key_of_shift in SHIFT_INTERVALS:
        if call.data == key_of_shift:
            delete_or_insert(call)
            msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=".",
                                        parse_mode='Markdown')
            create_inlinekeyboarb(msg)

if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling(True)
        except Exception as problem:
            print(problem.args)
            time.sleep(20)
