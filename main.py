from datetime import timedelta, date, datetime
from time import sleep

from appfunctions import APP
from browser import Browser
from config import logger, SCL_IMBALANCE_PAGE
from database.db_functions import DB

if __name__ == '__main__':

    APP.what_is_your_server()
    args = APP().app_argparser()  # отримуємо параметри, встановлені користувачем при запуску
    browser = Browser()

    # lst_arg_users = ['bipatov', 'ikozlovska']
    lst_arg_users = args.user
    print(lst_arg_users)
    lst_db_users = DB().get_info_users(lst_arg_users)
    lst_db_logins = [db.login for db in lst_db_users]
    absent_login = list(
        set(lst_arg_users).difference(lst_db_logins))  # які логіни вказані в параметрах запуску відсутні в БД?
    if absent_login:
        logger.error(f'ПОМИЛКА! В БД не знайдено логін користувача: {absent_login}')
        exit(f'ПОМИЛКА! В БД не знайдено логін користувача: {absent_login}')
    # lst_arg_users = args.users
    # lst_db_users = [User(login=SCL_USER, password=SCL_PASS, active=True, name='bipatovnam')]
    # lst_db_users = [User(login='h_hutsol', password=SCL_PASS, active=True, name='hhh')]
    for user in lst_db_users:
        browser.set_browser(True)  # False - visible browser. True - headless
        chrome: object = browser.get_browser()
        if chrome is not None:
            if not browser.login_scl(user):  # вхід користувача на сайт
                browser.close()
                exit()

            if user.login != 'bipatov':

                if not browser.check_role_existence(user, 'PROD'):  # перевірка чи перелік компанія-роль з БД є на сайті
                    browser.close()
                    exit()
                if not browser.check_role_existence(user, 'BRP'):  # перевірка чи перелік компанія-роль з БД є на сайті
                    browser.close()
                    exit()

                # ----------------------------- виконання по ролі PROD-------------------------------------------------
                for tov in user.companies:
                    browser.choose_company_role(user, tov.nickname, 'PROD')
                    tod = date.today()
                    info_label = tov.nickname + ' - PROD (' + user.login + ')'

                    # Генерація
                    delta_gen = args.generation
                    browser.run_perform(tod, delta_gen, 'GENERATION', 'PROD', info_label)

                    # Графік
                    delta_sch = args.schedule
                    browser.run_perform(tod, delta_sch, 'SCHEDULE', 'PROD', info_label)

                    # Споживання
                    delta_cns = args.consumption
                    browser.run_perform(tod, delta_cns, 'CONSUMPTION', 'PROD', info_label)

                # ----------------------------- виконання по ролі BRP -------------------------------------------------

                for tov in user.companies:
                    browser.choose_company_role(user, tov.nickname, 'BRP')
                    tod = date.today()
                    info_label = tov.nickname + ' - BRP (' + user.login + ')'

                    # Графік
                    delta_sch = args.schedule
                    browser.run_perform(tod, delta_sch, 'SCHEDULE', 'BRP', info_label)

                    # Доставка
                    delta_dlv = args.delivery
                    browser.run_perform(tod, delta_dlv, 'DELIVERY', 'BRP', info_label)

                    # Покупка
                    delta_pch = args.purchase
                    browser.run_perform(tod, delta_pch, 'PURCHASE', 'BRP', info_label)

            else:
                # ------------------------- bipatov виконання по ролі BRP----------------------------------------------
                if not browser.check_role_existence(user,'BRP'):  # перевірка чи перелік компанія-роль з БД є на сайті
                    browser.close()
                    exit()
                # browser.choose_company_and_role('SDE', 'BRP') #SDE ASD_LEKS
                for tov in user.companies:
                    browser.choose_company_role(user, tov.nickname, 'BRP')
                    tod = date.today()
                    info_label = tov.nickname + ' - BRP (' + user.login + ')'
                    # Графік
                    delta_sch = args.schedule
                    browser.run_perform(tod, delta_sch, 'SCHEDULE', 'BRP', info_label)

                    # Споживання
                    delta_cns = args.consumption
                    browser.run_perform(tod, delta_cns, 'CONSUMPTION', 'BRP', info_label)

                    # Вигрузка по небалансах
                    start_imb_date = datetime.strptime(args.imbalance, '%Y-%m-%d').date()
                    next_month = start_imb_date.replace(day=28) + timedelta(days=4)
                    end_imb_date = next_month - timedelta(days=next_month.day)  # по кінець місяця
                    browser.request_imbalance(start_imb_date, end_imb_date, SCL_IMBALANCE_PAGE)
                    is_connect = True

        else:
            print("chrome error")
            sleep(1)
            exit()
    browser.close()
    print('Bихід \n_______________________________')
