from itertools import chain

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from user_manage import *

bot = telebot.TeleBot("5718732573:AAFevR1k-m7LRs0ewts2CV1ZZ34sqJ9I8hk")


def get_pretty_collections(profile):
    return ''.join(
        f'\n⚫ {pare[0]} {pare[2]}' if pare[1] else f'\n⚪ {pare[0]} {pare[2]}' for pare in profile['collections'])


def get_pretty_notifications(profile):
    if profile['notifications']:
        return 'Включены'
    return 'Выключены'


@bot.message_handler(commands=['notifications'])
def notification(message):
    isprofile = if_profile_exists(message.from_user.id)
    if isprofile:
        d = read_profile_json()
        d[str(message.from_user.id)]['notifications'] = not d[str(message.from_user.id)]['notifications']
        save_profile_json(d)
        bot.send_message(message.from_user.id, f'Уведомления {get_pretty_notifications(d[str(message.from_user.id)])}')


@bot.message_handler(commands=['start', 'profile'])
def send_welcome(message):
    isprofile = if_profile_exists(message.from_user.id)
    if not isprofile:
        bot.send_message(message.from_user.id, "*Приветсвие*")
        profile = create_profile(message.from_user.id)

        bot.send_message(message.from_user.id,
                         f"""Выбраны настройки по умолчанию:\n\nУведомления: {get_pretty_notifications(profile)}\n\nВыбранные коллекции:{get_pretty_collections(profile)}\n\nКоличество первых трейдов: {profile['trades_limit']}""")
    else:
        profile = get_profile(message.from_user.id)
        bot.send_message(message.from_user.id,
                         f"""Ваши настройки:\n\nУведомления: {get_pretty_notifications(profile)}\n\nВыбранные коллекции:{get_pretty_collections(profile)}\n\nКоличество первых трейдов: {profile['trades_limit']}""")


@bot.message_handler(commands=['change_trades_limit'])
def change_trades_limit(message):
    bot.send_message(message.from_user.id, 'Введите целое число от 1 до 100')
    bot.register_next_step_handler(message, process_change_trades_limit)


def process_change_trades_limit(message):
    if not (str(message.text).isdigit() or str(message.text).isdecimal()):
        bot.send_message(message.from_user.id, 'Неверно. Введите целое число от 1 до 100')
        bot.register_next_step_handler(message, process_change_trades_limit)
    else:
        d = read_profile_json()
        d[str(message.from_user.id)]['trades_limit'] = int(message.text)
        save_profile_json(d)
        bot.send_message(message.from_user.id, f'Лимит изменён на {d[str(message.from_user.id)]["trades_limit"]}')


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


@bot.message_handler(commands=['change_collections'])
def change_trades_limit(message):
    isprofile = if_profile_exists(message.from_user.id)
    if not isprofile:
        bot.send_message(message.from_user.id, 'У вас нет профиля. Напишите /start')
    else:
        profile = get_profile(message.from_user.id)
        button_list = [
            InlineKeyboardButton(f'{col[0]} (Вкл.)', callback_data=f'onoff {col[0]} (Вкл.)') if col[
                1] else InlineKeyboardButton(f'{col[0]} (Выкл.)', callback_data=f'onoff {col[0]} (Выкл.)') for col in
            profile['collections']
        ]
        change_collection_values = [
            InlineKeyboardButton(f'< {col[2][0]} | > {col[2][1]}', callback_data=f'chvl {col[0]} _') for col in
            profile['collections']
        ]
        total_list = list(zip(button_list, change_collection_values, strict=True))
        total_list = list(chain.from_iterable(total_list))
        reply_markup = InlineKeyboardMarkup(build_menu(total_list, n_cols=2))
        bot.send_message(message.from_user.id, text="Ваши коллекции", reply_markup=reply_markup)


def change_lower_limit(message, col):
    try:
        float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, f'Неверно. Введите нижнюю границу для {col}:')
        bot.register_next_step_handler(message, lambda m: change_lower_limit(m, col))
    else:
        new_collectrtions = []
        d = read_profile_json()
        for c in d[str(message.chat.id)]['collections']:
            if c[0] == col:
                new_collectrtions.append([c[0], c[1], [float(message.text), c[2][1]]])
            else:
                new_collectrtions.append([c[0], c[1], c[2]])
        d[str(message.chat.id)]['collections'] = new_collectrtions
        save_profile_json(d)
        bot.send_message(message.chat.id, f'Введите верхнюю границу для {col}:')
        bot.register_next_step_handler(message, lambda m: change_upper_limit(m, col))


def change_upper_limit(message, col):
    try:
        float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, f'Неверно. Введите верхнюю границу для {col}:')
        bot.register_next_step_handler(message, lambda m: change_upper_limit(m, col))
    else:
        new_collectrtions = []
        d = read_profile_json()
        for c in d[str(message.chat.id)]['collections']:
            if c[0] == col:
                new_collectrtions.append([c[0], c[1], [c[2][0], float(message.text)]])
            else:
                new_collectrtions.append([c[0], c[1], c[2]])
        d[str(message.chat.id)]['collections'] = new_collectrtions
        save_profile_json(d)
        profile = get_profile(message.chat.id)
        button_list = [
            InlineKeyboardButton(f'{col[0]} (Вкл.)', callback_data=f'onoff {col[0]} (Вкл.)') if col[
                1] else InlineKeyboardButton(f'{col[0]} (Выкл.)', callback_data=f'onoff {col[0]} (Выкл.)') for col in
            profile['collections']
        ]
        change_collection_values = [
            InlineKeyboardButton(f'< {col[2][0]} | > {col[2][1]}', callback_data=f'chvl {col[0]} _') for col in
            profile['collections']
        ]
        total_list = list(zip(button_list, change_collection_values, strict=True))
        total_list = list(chain.from_iterable(total_list))
        reply_markup = InlineKeyboardMarkup(build_menu(total_list, n_cols=2))
        bot.send_message(message.from_user.id, text="Ваши коллекции", reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        state, col, pos = call.data.split()
        if state == 'chvl':
            bot.send_message(call.message.chat.id, f'Введите нижнюю границу для {col}:')
            bot.register_next_step_handler(call.message, lambda m: change_lower_limit(m, col))
        if state == 'onoff':
            if pos == '(Вкл.)':
                pos = False
            elif pos == '(Выкл.)':
                pos = True
            new_collectrtions = []
            d = read_profile_json()
            for c in d[str(call.message.chat.id)]['collections']:
                if c[0] == col:
                    new_collectrtions.append([c[0], pos, c[2]])
                else:
                    new_collectrtions.append([c[0], c[1], c[2]])
            d[str(call.message.chat.id)]['collections'] = new_collectrtions
            save_profile_json(d)
            profile = get_profile(call.message.chat.id)
            button_list = [
                InlineKeyboardButton(f'{col[0]} (Вкл.)', callback_data=f'onoff {col[0]} (Вкл.)') if col[
                    1] else InlineKeyboardButton(f'{col[0]} (Выкл.)', callback_data=f'onoff {col[0]} (Выкл.)') for col
                in
                profile['collections']
            ]
            change_collection_values = [
                InlineKeyboardButton(f'< {col[2][0]} | > {col[2][1]}', callback_data=f'chvl {col[0]} _') for col in
                profile['collections']
            ]
            total_list = list(zip(button_list, change_collection_values, strict=True))
            total_list = list(chain.from_iterable(total_list))
            reply_markup = InlineKeyboardMarkup(build_menu(total_list, n_cols=2))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Ваши коллекции",
                                  reply_markup=reply_markup)



def turn_on_bot():
    bot.infinity_polling()


if __name__ == "__main__":
    turn_on_bot()
