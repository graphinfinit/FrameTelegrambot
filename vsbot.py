"""
@framebot (телеграм бот для записи людей на определенное время)

"""
import telebot
from telebot import types

import time
from datetime import datetime, timedelta
import re

from settings import *
from dbclass import *

bot = telebot.TeleBot(TOKEN, threaded=False)  # отключена многопоточность библиотеки threaded=False
print('Start program...{}'.format(datetime.now()))

# Сразу создадим таблицы
initdb = SqliteDb()
initdb.create_table()
initdb.create_config_table()
initdb.create_limittable()
initdb.create_timetable()
initdb.close()


print('Ok...')



def is_allowed(string):
    characherRegex = re.compile(r'[^a-zA-Z0-9.:\s]')
    string = characherRegex.search(string)
    return not bool(string)


def get_shift_intervals(goodsymbol=GoodSymbol, default_value=SHIFT_INTERVALS):
    try:
        connect = SqliteDb()
        rows = connect.get_configs()
        connect.close()

        SHIFT_INTERVALS = {}
        for row in rows:
            q = dict(row)
            SHIFT_INTERVALS[str(q['id'])] = goodsymbol + q['shift']
        if bool(SHIFT_INTERVALS):
            return SHIFT_INTERVALS
        else:
            return default_value
    except Exception as exc:
        print(exc.args)


def get_shiftmax(default_value=SHIFTMAX):
    try:
        connect = SqliteDb()
        dt = connect.get_max()
        connect.close()
        dt = dict(dt[0])
    except Exception as exc:
        print(exc.args)

    if dt:
        if dt['vlimit'].isdigit():
            return int(dt['vlimit'])
    else:
        return default_value

def get_time():
    connect = SqliteDb()
    lim = connect.get_timelimit()
    connect.close()

    f = dict(lim[0])
    timestart = f['timestart']
    timelimit = f['timelimit']
    try:

        timestart = datetime.strptime(timestart, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=3)
        timeend = timestart + timedelta(minutes=int(timelimit))
    except Exception as exc:
        print(exc.args)
    return [timestart, timeend]







def create_inlinekeyboarb(message):
    SHIFTMAX = get_shiftmax()
    SHIFT_INTERVALS = get_shift_intervals()
    limlist = get_time()
    db = SqliteDb()
    inlinekeyboarb = types.InlineKeyboardMarkup(row_width=2)

    for shift in SHIFT_INTERVALS:
        text = SHIFT_INTERVALS[shift]
        us = len(db.count_rows(shift=shift))
        if us == SHIFTMAX:
            text = SHIFT_INTERVALS[shift] + " ❌ Запись закрыта"

        itembtnlook = types.InlineKeyboardButton(text='Участники {}/{} 🙋'.format(us, SHIFTMAX), callback_data=shift+'_look')
        itembtn1 = types.InlineKeyboardButton(text=text, callback_data=shift)

        inlinekeyboarb.row(itembtnlook, itembtn1)
    db.close()
    bot.send_message(message.chat.id,
                     text="Запись на завтра открыта 🥁🥁 Выбираем время ➡.Успейте записаться с {} по {}️ по Мск".format(str(limlist[0]),str(limlist[1])),
                     reply_markup=inlinekeyboarb)

def delete_or_insert(call):
    """
    :param call: принимает данные из инлайн-клавиатуры
    :return: answer_callback_query  Делает запрос в БД и показавает всплывающее окно об удаление или добавлении записи.
    """
    SHIFTMAX = get_shiftmax()
    SHIFT_INTERVALS = get_shift_intervals()
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
            try:
                user_name = call.from_user.first_name + '_' + call.from_user.last_name
            except Exception:
                user_name = 'Безымянный'

            status = db.insert(shift=call.data, user_id=call.from_user.id, user_name=user_name,
                               date=datetime.now())

            db.close()
            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text="{}, Вы записаны на {}. Нажмите еще раз если хотите отписаться".format(call.from_user.first_name,
                                                                                    SHIFT_INTERVALS[call.data]))

@bot.message_handler(func=lambda m: True)
def process_main(message):
    SHIFT_INTERVALS = get_shift_intervals()
    if message.text == '/start':
        create_inlinekeyboarb(message)

    elif message.text == '/help':
        text = """Дамы и господа! Я обычный бот для записи.
        Мои основные команды:
          /start - вывести окно записи
          /look - посмотреть всех записавшихся 
        Функционал доступный только администратору:
          /push - удалить всех записавшихся, отобразить новое пустое окно записи, обнулить время начала записи.
          /config - редактировать окно записи(после config перечислите названия смен через пробел):
        Для отложенного запуска окна записи:
           -наберите команды и удерживайте кнопку _отправить_ > в мобильной версии
           или правой кнопкой мыши в десктопе
          /max - максимальное количество записей на одну смену
          /timelimit - установить время действие окна записи в минутах.По умолчанию 240минут(4 часа)
           
           @graphinfinit
           
        """
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJIzV6ZAxBrxUQi0nrkXj1UrbMCRtIuAAJxbAACY4tGDL3Mn3hoWa1cGAQ')
        bot.send_message(message.chat.id,
        text=text)

    elif message.text == '/look':
        db = SqliteDb()
        for shift in SHIFT_INTERVALS:
            count_rows = db.count_rows(shift=shift)
            bot.send_message(message.chat.id,
                             text='Записались на {} - {} человек.'.format(SHIFT_INTERVALS[shift], len(count_rows)))
            for row in count_rows:
                row = dict(row)
                text ="<a href='tg://user?id={}'>{}</a>".format(row['user_id'], row['user_name'])
                bot.send_message(message.chat.id, text=text, parse_mode='HTML')
        db.close()

    elif message.text == '/push':
        if str(message.from_user.id) in ADMIN_LIST:
            db = SqliteDb()
            db.drop_table()
            db.create_table()
            db.update_timestart(timestart=datetime.now())

            db.close()
            bot.send_message(message.chat.id, text="<strong>.</strong>".format(
                message.from_user.first_name), parse_mode='HTML')
            create_inlinekeyboarb(message)
        else:
            bot.send_message(message.chat.id, text="<strong>!{}, я слушаюсь только хозяина.</strong>".format(message.from_user.first_name), parse_mode='HTML')

    elif message.text[:7] == '/config':
        if str(message.from_user.id) in ADMIN_LIST:
            try:
                data = message.text[8:]
                if is_allowed(data) and len(data) > 2:
                    shift_list = message.text[8:].split()
                    db = SqliteDb()
                    db.drop_config()
                    db.create_config_table()
                    for shift in shift_list:
                        db.insert_config(shift=shift)
                    db.close()

                    bot.send_message(message.chat.id, text="{}, Данные были обновлены!!!".format(
                        message.from_user.first_name))
                else:
                    bot.send_message(message.chat.id,
                    text="Ошибка. В названии интервала допустимы только цифры, буквы и двоеточие ':'")

            except:
                bot.send_message(message.chat.id,
                text="Ошибка. Придерживайтесь формата /config[пробел]Название интервала[пробел]Название интервала 2...")
        else:
            bot.send_message(message.chat.id, text="<strong>!{}, я слушаюсь только хозяина.</strong>".format(message.from_user.first_name), parse_mode='HTML')

    elif message.text[:4] == '/max':
        if str(message.from_user.id) in ADMIN_LIST:
            try:
                data = message.text[5:]
                if data.isdigit():
                    if int(data) >= 1:
                        db = SqliteDb()
                        db.drop_max()
                        db.create_limittable()
                        db.set_max(data)
                        db.close()
                        bot.send_message(message.chat.id,
                                         text="Наверное получилось...")
                else:
                    bot.send_message(message.chat.id,
                                     text="Ошибка входных данных.")
            except Exception:
                bot.send_message(message.chat.id,
                                 text="Ошибка!!")
    elif message.text[:10] == '/timelimit':
        if str(message.from_user.id) in ADMIN_LIST:
            if message.text[11:].isdigit():
                try:
                    timelimit = message.text[11:]
                    db = SqliteDb()
                    db.update_timelimit(timelimit=timelimit)
                    db.close
                    bot.send_message(message.chat.id,
                                     text="Ограничение по времени успешно обновлено")
                except Exception as exc:
                    print(exc.args)
            else:
                bot.send_message(message.chat.id,
                                 text="Неправильные данные. Введите число после команды")

        else:
            bot.send_message(message.chat.id, text="<strong>!{}, я слушаюсь только хозяина.</strong>", parse_mode='HTML')



    else:
        pass


@bot.callback_query_handler(func=lambda call: True)
def process_call(call):
    SHIFT_INTERVALS = get_shift_intervals()
    lim = get_time()
    timeend = lim[1]
    timenow = datetime.now() + timedelta(hours=3)



    for key_of_shift in SHIFT_INTERVALS:
        if call.data == key_of_shift:
            if timeend > timenow:
                delete_or_insert(call)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                create_inlinekeyboarb(call.message)
            else:
                bot.answer_callback_query(callback_query_id=call.id,
                                          show_alert=True,
                                          text='К сожалению время записи истекло. Попробуйте в другой раз')


        if call.data == key_of_shift + '_look':
            db = SqliteDb()
            count_rows = db.count_rows(shift=key_of_shift)
            text = 'Записались {} человек:  '.format(len(count_rows))
            for row in count_rows:
                row = dict(row)
                text += "  {}  ".format(row['user_name'])
            db.close()

            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text=text)

if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling(True)
        except Exception as problem:
            print(problem.args)
            time.sleep(20)
