import argparse
from datetime import datetime, timedelta
from enum import Enum

import numpy as np
import pandas
import pytz

from appclasses import DbComponent, SiteComponent
from config import logger, SCL_TIME_DELTA_DAYS, SCL_START_IMBALANCE_DATE, USE_SSH, SSH_HOST, DEFAULT_SCHEMA, SCL_USER
from database.db_functions import DB


# def what_is_your_server():
#     if USE_SSH == 1 and SSH_HOST == '185.168.129.104':
#         print("--- ONLINE server ---")
#     elif USE_SSH == 1 and SSH_HOST == '46.164.150.162':
#         print("--- TEST server ---")
#     else:
#         print("--- UNKNOWN server ---")


class APP:

    def __init__(self):
        pass
        # APP.what_is_your_server()

    @staticmethod
    def what_is_your_server():

        if USE_SSH == 1 and SSH_HOST == '185.168.129.104':
            print(f"--- ONLINE server --- schema {DEFAULT_SCHEMA}")
        elif USE_SSH == 1 and SSH_HOST == '46.164.150.162':
            print(f"--- TEST server --- schema {DEFAULT_SCHEMA}")
        else:
            print("--- UNKNOWN server ---")

    def app_argparser(self):

        # APP.what_is_your_server()
        def list_of_str(arg):
            return list(map(str, arg.split(',')))

        argparser = argparse.ArgumentParser(description='Параметри для запуску застосунку. Приклад, '
                                                        'py main.py --user=bipatov,h_hutsol --schedule=12 '
                                                        '--consumption=5 --imbalance=2023-09-04')

        argparser.add_argument(
            '--user',
            type=list_of_str,
            # nargs='*',  # даний аргумент може приймати ніодного, одне або декілька значень
            default=SCL_USER,
            help='Логін користувача для входу на сайт. Якщо параметр не встановлений, '
                 'буде використане значення SCL_USER з файлу env.env')

        argparser.add_argument(
            '--schedule',
            type=int,
            default=SCL_TIME_DELTA_DAYS,
            help='Кількість попередніх днів для вивантаження торгових графіків. Якщо параметр не встановлений, '
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--consumption',
            type=int,
            default=SCL_TIME_DELTA_DAYS,
            help='Кількість попередніх днів для вивантаження споживання. Якщо параметр не встановлений, '
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--generation',
            type=int,
            default=SCL_TIME_DELTA_DAYS,
            help='Кількість попередніх днів для вивантаження генерації. Якщо параметр не встановлений, '
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--purchase',
            type=int,
            default=SCL_TIME_DELTA_DAYS,
            help='Кількість попередніх днів для вивантаження покупки. Якщо параметр не встановлений, '
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--delivery',
            type=int,
            default=SCL_TIME_DELTA_DAYS,
            help='Кількість попередніх днів для вивантаження доставки. Якщо параметр не встановлений, '
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--imbalance',
            type=str,
            default=SCL_START_IMBALANCE_DATE,
            help='Початкова дата для вивантаження розрахунку небалансів. Кінцева дата встановлюється автоматично - останній '
                 'день місяця від початкової дати.')
        args = argparser.parse_args()
        try:
            # Try to parse the string as a date with the "Y-m-d" format
            datetime.strptime(args.imbalance, "%Y-%m-%d")
        except ValueError:
            # If parsing fails, it's not in the correct format
            logger.error(f"{args.imbalance} Некоректний формат дати (Y-m-d).")
            exit(f"{args.imbalance} Некоректний формат дати (Y-m-d).")
        return args

    def report_argparser(self):
        class Enumtype(Enum):
            schedule = 'schedule'
            consumption = 'consumption'

            def __str__(self):
                return self.value

        class Enumversion(Enum):
            v1 = '1'
            v2 = '2'
            v3 = '3'

            def __str__(self):
                return self.value

        argparser = argparse.ArgumentParser(description='Параметри для формування звіту. Приклад: py reports.py '
                                                        '--reptype=schedule --fromdate=2023-09-01 --todate=2023-09-30'
                                                        ' --direction=from --version=1')

        argparser.add_argument(
            '--reptype',
            type=str,
            default=None,
            required=True,
            help='Тип звіту є два варіанта графік: schedule, споживання: consumption'
                 'буде використане значення SCL_TIME_DELTA_DAYS з файлу env.env')
        argparser.add_argument(
            '--fromdate',
            type=str,
            default=None,
            required=True,
            help='Початкова дата формування звіту, повинна бути у форматі yyyy-mm-dd')
        argparser.add_argument(
            '--todate',
            type=str,
            default=None,
            required=True,
            help='Кінцева дата формування звіту, повинна бути у форматі yyyy-mm-dd')
        argparser.add_argument(
            '--direction',
            type=str,
            default=None,
            required=False,
            help='Тип трейдингу, приймає два значення: від KNESS - from, до KNESS - to')
        argparser.add_argument(
            '--version',
            type=str,
            default=None,
            required=True,
            help='версія (1,2,3)')
        args = argparser.parse_args()
        try:
            # Try to parse the string as a date with the "Y-m-d" format
            stdt = datetime.strptime(args.fromdate, "%Y-%m-%d")
            endt = datetime.strptime(args.todate, "%Y-%m-%d")
        except ValueError:
            # If parsing fails, it's not in the correct format
            logger.error("Звіт. Некоректний формат дати (Y-m-d).")
            exit("Звіт. Некоректний формат дати (Y-m-d).")
        return args

    def check_component(self, table) -> bool:
        list_df = pandas.read_html(str(table))  # create dataframe from html
        col_df = list_df[0]
        # data_df = list_df[1]
        # data_df.columns = col_df.columns
        try:
            data_df = list_df[1]  # нові роки
            data_df.columns = col_df.columns
        except IndexError:
            data_df = list_df[
                0]  # старі роки (при викачці даних за минулі роки виявилось що дані мали іншу структуру ніж зараз)

        if len(data_df) == 0:  # якщо датафрейм пустий
            print(f'ПУСТИЙ ПЕРЕЛІК КОМПОНЕНТІВ БАЛАНСУВАННЯ')
            logger.info(f'ПУСТИЙ ПЕРЕЛІК КОМПОНЕНТІВ БАЛАНСУВАННЯ')
            return False

        data_df.drop(data_df.columns[[3, 8, 9, 10, 11]], axis=1, inplace=True)
        data_df.rename(columns={'UID': 'uid', 'Код ТКО': 'tko', 'Тип компонента': 'type_c',
                                'Від ОЕР 1 (відпуск)': 'pea_from', 'До ОЕР 2': 'pea_to',
                                'Дійсно з': 'valid_from', 'Дійсно до': 'valid_to'}, inplace=True)
        data_df['valid_from'] = pandas.to_datetime(data_df['valid_from'], dayfirst=True)
        data_df['valid_to'] = pandas.to_datetime(data_df['valid_to'], dayfirst=True)
        data_df.replace({pandas.NaT: None}, inplace=True)
        lst_site_components = []
        for x in data_df.itertuples():
            valid_from = x.valid_from
            valid_to = x.valid_to
            if valid_from is not None:
                valid_from = valid_from.date()
            if valid_to is not None:
                valid_to = valid_to.date()
            lst_site_components.append(
                SiteComponent(
                    x.uid, x.tko, x.type_c, x.pea_from, x.pea_to, valid_from, valid_to
                )
            )
        lst_db_components = DB().get_all_components()
        lst_new_components = []

        db_uid = [db.uid for db in lst_db_components]
        for site in lst_site_components:
            if site.uid not in db_uid:
                lst_new_components.append(site)
        if lst_new_components:  # є нові компоненти, будемо додавати в таблицю mms_dict_components

            lst_db_accounts = DB().get_all_accounts()  # перевіримо чи є нові ОЕР (енергетичні рахунки - accounts)
            lst_new_accounts, lst_new_acc_nicknames = [], []
            db_acc_nicknames = [db.nickname for db in
                                lst_db_accounts]  # наявний перелік значень pea з таблиці mms_dict_accounts

            for cmp in lst_new_components:  # формуємо перелік нових ОЕР для створення компонентів
                if cmp.pea_from not in db_acc_nicknames:
                    lst_new_acc_nicknames.append(cmp.pea_from)
                if cmp.pea_to not in db_acc_nicknames:
                    lst_new_acc_nicknames.append(cmp.pea_to)

            if lst_new_acc_nicknames:  # є нові ОЕР, будемо додавати
                lst_new_acc_nicknames = list(dict.fromkeys(lst_new_acc_nicknames))  # remove duplicates
                for new_nickname in lst_new_acc_nicknames:
                    lst_new_accounts.append(dict(nickname=new_nickname, active=True))
                lst_result = DB().add_accounts(lst_new_accounts)  # додамо нових ОЕРів
                if lst_result:
                    nick = [x.nickname for x in lst_result]
                    print(f"Додано нові ОЕРи:\n{nick}\n !!! Потрібно створити прив'язку до довідника компаній "
                          f"mms_dict_companies")
                    logger.info(f"Додано нові ОЕРи:\n{nick}\n !!! Потрібно створити прив'язку до довідника компаній "
                                f"mms_dict_companies")
                lst_db_accounts = DB().get_all_accounts()  # перевибиремо перелік ОЕРів з БД

            # маючи перелік нових компонентів та перелік ОЕРів, формуємо список для инсерту в таблицю
            # mms_dict_components (uid, tko, account_id_from, account_id_to, component_type_id, valid_from, valid_to
            lst_insert_components = []
            lst_db_component_types = DB().get_all_component_types()  # вибир перелік типів компонентів з БД, з нього
            # візьмемо component_type_id
            for x in lst_new_components:
                acc_id_from, acc_id_to, component_type_id = 0, 0, 0
                for i in lst_db_accounts:
                    if i.nickname == x.pea_from:
                        acc_id_from = i.id_
                    if i.nickname == x.pea_to:
                        acc_id_to = i.id_
                for t in lst_db_component_types:
                    if t['name'] == x.type_c:
                        component_type_id = t['id']
                        break

                lst_insert_components.append(dict(uid=x.uid, tko=x.tko, account_id_from=acc_id_from,
                                                  account_id_to=acc_id_to, component_type_id=component_type_id,
                                                  valid_from=x.valid_from, valid_to=x.valid_to
                                                  )
                                             )
            lst_result = DB().add_components(lst_insert_components)  # додаємо нові компоненти балансування
            if lst_result:
                new_uids = [x.uid for x in lst_result]
                new_tkos = [x.tko for x in lst_result]
                print(f'Додано нові компоненти балансування:\n{new_uids} - {new_tkos}')
                logger.info(f'Додано нові компоненти балансування:\n{new_uids} - {new_tkos}')
        return True

    def prepare_time_values(self, table, tko_uid_dict):  # , version

        list_df = pandas.read_html(str(table), thousands=' ')  # create dataframe from html
        col_df = list_df[3]  # date and hour
        data_df = list_df[4]  # values
        # name_df = list_df[2]  # names tko and other
        # name_df = name_df.drop(labels=[1, 2, 3, 4], axis=0)  # видаляєм зайві рядки з шапки

        data_df = data_df.applymap(lambda x: x.replace(',', '.'))
        data_df = data_df.replace('\xa0', '', regex=True)  # заміна пробілу
        data_df.replace(to_replace='f', value=None, inplace=True)  # '"F@'
        data_df.replace(to_replace='ff', value=None, inplace=True)
        data_df = data_df.replace(r'f$', 0, regex=True) #  заміна числа 13.0000f, 238.0000f, 7.0000f

        data_df = data_df.astype(float)
        data_df = data_df.replace(np.nan, None)

        col_df.columns = ['all']
        col_df[['date_meter', 'hour_from', 'hyphen', 'hour_to']] = col_df['all'].str.split(' ', expand=True)
        col_df.drop(['all', 'hyphen'], axis=1, inplace=True)
        col_df["hour_from"] = col_df["hour_from"].map(lambda x: int(x[:2]))
        col_df["hour_to"] = col_df["hour_to"].map(lambda x: int(x[:2]))
        col_df[['hour_from', 'hour_to']] = col_df[['hour_from', 'hour_to']].astype(int)
        col_df['date_meter'] = pandas.to_datetime(col_df['date_meter'], dayfirst=True)

        value_df = pandas.concat([col_df, data_df], axis=1, join='inner')

        lst_insert = []
        for row in value_df.itertuples(index=False):
            date_meter = row.date_meter
            date_meter = date_meter.date()  # datetime to date

            uid_lst = list(tko_uid_dict.values())  # перелік uid взятий зі сторінки Компоненти балансування
            # tko_lst = list(tko_uid_dict.keys())   # перелік назв відповідних до uid
            lenght_r = len(row)  # довжина кількість колонок датафрейму з даними. Перші 3 колонки дата, год з, год по
            i = 3
            uid_index = 0
            # version = int(version)
            vi = 1  # (всі версії) 123 123 123 123
            while i < lenght_r:
                # print(f'~~~~~~~~ {vi} ~~~~~~~~~~~')
                # print(f'{row.date_meter}---{row.hour_from}---{row.hour_to}***{row[i]}/////{uid_lst[uid_index]}______')
                lst_insert.append(dict(component_uid=uid_lst[uid_index], version_id=vi, date_meter=date_meter,
                                       hour_from=row.hour_from, hour_to=row.hour_to, value_meter=row[i]
                                       )
                                  )
                i += 1

                if vi < 3:
                    vi += 1
                else:
                    vi = 1
                    uid_index += 1

        return lst_insert

    def prepare_imbalance(self, data_list):
        lst_insert = []
        if not data_list:
            return lst_insert  # немає даних
        df = pandas.DataFrame(data_list)
        df.dropna(subset=['quantity'], inplace=True)  # видаляємо рядки, де в колонці кількість небалансу nan
        df = df[df['quantity'] != 0]  # видаляємо рядки, де в колонці кількість небалансу 0
        if df.empty:
            return lst_insert  # немає даних
        else:
            df["imsp"] = df["imsp"].fillna(0)
            df["amount"] = df["amount"].fillna(0)
            lst_db_type_imb = DB().get_types_imbalance()
            prev_tup_date_hour_1 = 0
            prev_tup_date_hour_2 = 0
            for row in df.itertuples(index=False):
                type_id = 0
                lst_date_hours = self.change_timezone(row.timeStart)
                # якщо маємо ознаку переходу на зим.час з функції change_timezone і попередня почасовка була 2-3,
                # то поточну робимо 3-3
                if lst_date_hours[
                    3] == 1 and prev_tup_date_hour_1 == 2 and prev_tup_date_hour_2 == 3:  # перехід на зимовий час
                    lst_date_hours[2] -= 1
                # print(f'{lst_date_hours[0]}---{lst_date_hours[1]}---{lst_date_hours[2]}')
                for i in lst_db_type_imb:
                    if i.name_en_direction == row.direction:
                        type_id = i.id_

                lst_insert.append(dict(type_id=type_id, date_calc=lst_date_hours[0], hour_from=lst_date_hours[1],
                                       hour_to=lst_date_hours[2], imbalance_amount=row.quantity, imsp_price=row.imsp,
                                       rdn_price=row.prDam, payment_price=row.price, payment_sum=row.amount)
                                  )
                prev_tup_date_hour_1 = lst_date_hours[1]
                prev_tup_date_hour_2 = lst_date_hours[2]
        return lst_insert

    def change_timezone(self, date_in_iso_8601: str) -> list[str, int, int, int]:
        # перехід на зимовий (ост. неділя жовтня, мають бути такі години 2-3, 3-3, 3-4) а система видає 2-3, 3-4, 3-4
        # перехід на літній  (ост. неділя березня, мають бути такі години 2-3, 4-5, 5-6) так і дає, нічого не робимо
        # switch_time: за замовчуванням = 0, перехід на зимовий = 1
        switch_time = 0
        # dt_str = "2023-08-03T21:00:00Z"  # Input ISO-8601 date and time string
        dt = datetime.fromisoformat(date_in_iso_8601)  # Parse the ISO-8601 string into a datetime object
        gmt_plus_3 = pytz.timezone('Europe/Kyiv')  # Define the GMT+3 timezone
        dt_gmt_plus_3 = dt.replace(tzinfo=pytz.utc).astimezone(gmt_plus_3)  # Convert the datetime to the GMT+3 timezone
        date_gmt_plus_3 = dt_gmt_plus_3.strftime("%Y-%m-%d")
        start_time_gmt_plus_3 = dt_gmt_plus_3.strftime("%H")
        # встановимо признак переходу на зим.час, якщо у нас відповідна дата і 3тя година
        if (dt_gmt_plus_3.month == 10 and dt_gmt_plus_3.strftime('%A') == 'Sunday' and dt_gmt_plus_3.day > 24 and
                (int(start_time_gmt_plus_3)) == 3):
            switch_time = 1
        end_time_gmt_plus_3 = (dt_gmt_plus_3 + timedelta(hours=1)).strftime("%H")

        return [date_gmt_plus_3, int(start_time_gmt_plus_3), int(end_time_gmt_plus_3), switch_time]
