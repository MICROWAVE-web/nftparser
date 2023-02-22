# from threading import *
import json
import os
from multiprocessing import Process
import time
import schedule
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from bot import turn_on_bot, bot
from user_manage import *

trade_json = 'data/trade.json'


def read_trade_json():
    with open(trade_json, encoding='utf-8') as f:
        d = json.load(f)
    return d


def save_trade_json(data=None, new=False):
    if data is None and new is True:
        data = {}
    if data is None and new is False:
        raise Exception('Incorrect save_json!')
    with open(trade_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_operations(urladress, webdrive):
    webdrive.get(urladress)
    time.sleep(1)
    layouts = webdrive.find_elements(By.CLASS_NAME, 'np-layout-switch__selector')
    layouts[1].click()
    time.sleep(0.5)
    result = webdrive.find_element(By.CLASS_NAME, 'MuiTableBody-root').text.split('\n')
    return result


def check_operations(urls):
    webdrive = get_driver()
    for url in urls:
        operations_data = get_operations(url, webdrive)
        operations_data = [[operations_data[i], operations_data[i + 1].split()[0], operations_data[i + 1].split()[1]]
                           for i in range(0, len(operations_data) - 1, 2)]
        title = url.split('/')[-1]
        d = read_trade_json()
        d[title] = operations_data
        save_trade_json(d)
    webdrive.quit()


def check_trades():
    dp = read_profile_json()
    dt = read_trade_json()
    for user_key in dp.keys():
        if not dp[user_key]['notifications']:
            continue
        limit = dp[user_key]['trades_limit']
        context = {}
        for trade_key in dt.keys():
            context[trade_key] = 0
            for trade in dt[trade_key][:limit]:
                context[trade_key] += float(trade[2])
            context[trade_key] = round(context[trade_key], 6)
        for c in dp[user_key]['collections']:
            if c[1] and context.get(c[0]) and (context[c[0]] < c[2][0] or c[2][1] < context[c[0]]):
                if dp[user_key]['last'].get(c[0]) and context[c[0]] == dp[user_key]['last'][c[0]]:
                    continue
                else:
                    bot.send_message(user_key, f'{c[0]}: {context[c[0]]}')
                    dp[user_key]['last'][c[0]] = context[c[0]]
                    save_profile_json(dp)


'''            else:
                try:

                    print(c[0], context, c[2][0], c[2][1])
                except KeyError:
                    pass'''


def start_scheduler(url_adresses):
    schedule.every(1).seconds.do(lambda: check_operations(url_adresses))
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_notification_scheduler():
    schedule.every(1).seconds.do(lambda: check_trades())
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_driver():
    chromeOptions = uc.ChromeOptions()
    chromeOptions.add_argument("--headless=new")
    dr = uc.Chrome(options=chromeOptions)
    return dr


if __name__ == '__main__':
    newpath = r'data'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    save_trade_json(new=True)
    if not os.path.exists(user_file):
        save_profile_json(new=True)
    urls = [i.strip() for i in open('urls.txt').readlines()]
    Process(target=turn_on_bot).start()
    thread_parser = Process(target=start_scheduler, args=(urls,))
    thread_notification = Process(target=start_notification_scheduler)
    thread_notification.start()
    thread_parser.start()
    thread_notification.join()
    thread_parser.join()

