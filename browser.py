import time
from datetime import timedelta
from time import sleep

import pandas

from appfunctions import APP
from config import SCL_HOST, SSH_HOST, USE_SSH
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException, InvalidSessionIdException
from urllib3.exceptions import MaxRetryError
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from database.db_functions import *
import json


class Browser:
    list_options = [
        '--no--sandbox', '--disable-gpu', '--disable-software-rasterizer',
        'start-maximized', 'disable-infobars', 'disable-extensions', '--log-level=3',  # --log-level=2-warning, 1-error
    ]

    def __init__(self):
        self.__browser = None

    def set_browser(self, headless: bool):
        options = Options()
        options.add_argument("window-size=1280,720")
        options.headless = headless
        # logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
        # loggerw = logging.getLogger()
        for opt in self.list_options:
            options.add_argument(opt)
        try:
            self.__browser = webdriver.Chrome(options=options)
        except WebDriverException as ex:
            logger.error(str(ex))
            print(str(ex))

    def get_browser(self) -> webdriver.Chrome | None:
        return self.__browser

    def to_check_ready(self, locator_method, find_string: str):

        # variants of locator_method: By.XPATH, By.ID, By.CLASSNAME

        # tic = time.perf_counter()
        element = WebDriverWait(self.__browser, 15).until(
            EC.presence_of_element_located((locator_method, find_string))
        )
        # toc = time.perf_counter()
        if element:
            # print(f'element located SUCSESS in {round(toc - tic, 2)} second')
            # tic = time.perf_counter()
            element = WebDriverWait(self.__browser, 15).until(
                EC.element_to_be_clickable((locator_method, find_string))
            )
            # toc = time.perf_counter()
            if element:
                # print(f'element clickable SUCSESS in {round(toc - tic, 2)} second')
                return element
        print('функція to_check_ready - return None ')
        return None

    def login_scl(self, user: User) -> bool:
        # self.set_browser(False)  # False - visible browser. True - headless
        # if not self.__browser or self.__browser is None:
        #     return None
        try:
            print(f'Користувач {user.login}: вхід на платформу по логін-паролю')

            # Обираємо тип входу по логін-паролю
            self.__browser.get('{host}/'.format(host=SCL_HOST))
            self.to_check_ready(By.XPATH, '//*[@id="mat-expansion-panel-header-0"]').click()
            # Виконуємо вхід
            self.to_check_ready(By.ID, 'mat-input-0').send_keys(user.login)
            self.to_check_ready(By.ID, 'mat-input-1').send_keys(user.password)
            self.to_check_ready(By.XPATH, '/html/body/mms-root/mms-simple-layout/mms-login/div'
                                          '/mat-card/div/mat-expansion-panel/div/div/div/button').click()
            sleep(4)
            # Якщо відкрилась сторінка https://mms.ua.energy/welcome , то залогінились успішно
            if self.__browser.current_url == 'https://mms.ua.energy/welcome':
                logger.info("Вхід виконано... " + self.__browser.current_url)
                print('Вхід виконано ' + self.__browser.current_url +
                      '\n---------------------------')
                return True
            else:
                logger.error("Не вдалось увійти на сайт " + self.__browser.current_url)
                print('Не вдалось увійти на сайт ' + self.__browser.current_url)
                return False

        except (NoSuchElementException, WebDriverException) as ex:
            print(str(ex))
            logger.error(str(ex))
            exit("ERROR in login_scl function: No such element. Change structure site OR No connect!!!")

    # перевіряємо чи команії - ролі з БД присутні в переліку компаній-ролей користувача на сайті
    def check_role_existence(self, user: User, role) -> bool:
        lst_absent_roles = []
        lst_db_role = [c.nickname + ' - ' + role for c in user.companies]  # список компаній поточного користувача з БД
        self.to_check_ready(By.ID, "mat-select-1").click()
        sleep(1)
        site_roles = self.__browser.find_elements(By.CLASS_NAME, "mat-option")

        lst_site_role = [w.text for w in site_roles]  # список компаній поточного користувача на сайті

        for d in lst_db_role:
            try:
                s = lst_site_role.index(d)
            except ValueError:
                lst_absent_roles.append(d)
        # щоб закрився список компанії-ролі оновити сторінку
        self.to_check_ready(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[1]/a').click()
        if lst_absent_roles:
            print(f'Помилка! Роль {lst_absent_roles} користувача {user.login} відсутня на сайті')
            logger.error(f' Помилка! Роль {lst_absent_roles} користувача {user.login} відсутня на сайті')
            return False
        else:
            return True

    def choose_company_role(self, user, company, role):  # tov.nickname, 'BRP'

        try:
            self.__browser.switch_to.default_content()
            self.to_check_ready(By.ID, "mat-select-1").click()
            find_string = r"//*[contains(text(),'" + company + " - " + role + "')]"
            # print(find_string)
            r = (self.__browser.find_element(By.XPATH, find_string))

            selected_el = self.__browser.find_element(By.CSS_SELECTOR, 'mat-option[aria-selected="true"]')
            if selected_el.text != company + ' - ' + role:  # якщо потрібна роль уже вибрана - не клікаєм на неї
                r.click()
            sleep(2)
            print(f'Обрали компанію-роль {company} - {role} ({user.login})')
            # після вибору компанії-ролі оновити сторінку
            self.to_check_ready(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[1]/a').click()
            sleep(3)
            # print('Формуємо перелік компонентів балансування')
            # Відкриваємо меню Балансування -> Результати балансування -> Компоненти балансування
            b = self.to_check_ready(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[5]/button')
            ActionChains(self.__browser).move_to_element(b).perform()
            b.click()
            # print('Балансування')
            r = self.to_check_ready(By.XPATH, '/html/body/div[2]/div[2]/div/div/div/div/button')
            r.click()
            # print('Результати балансування')
            k = self.to_check_ready(By.XPATH, '/html/body/div[2]/div[3]/div/div/div/span/button[1]')
            ActionChains(self.__browser).move_to_element(k).perform()
            k.click()

            print('Вибрали меню Компоненти балансування')
            # Переключаємось на iframe що містить дані
            frame = self.to_check_ready(By.CLASS_NAME, 'emfamily-frame')
            self.__browser.switch_to.frame(self.__browser.find_element(By.CLASS_NAME, 'emfamily-frame'))
            print('Переключились на iframe')
            # driver.switch_to.default_content()
        except (NoSuchElementException, WebDriverException) as ex:
            print(str(ex))
            logger.error(str(ex))
            self.__browser.close()
            exit("ERROR in choose_company_role function: No such element. Change structure site OR No connect!!!")

    def open_page_of_components(self):
        try:

            self.__browser.refresh()
            print("Browser refresh...")
            ###########https: // mms.ua.energy / emfamily / ComponentResultList.do
            # після вибору компанії-ролі оновити сторінку
            self.to_check_ready(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[1]/a').click()
            # self.__browser.find_element(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[1]/a').click()
            sleep(3)
            print('Формуємо перелік компонентів балансування')
            # Відкриваємо меню Балансування -> Результати балансування -> Компоненти балансування
            b = self.to_check_ready(By.XPATH, '//*[@id="navbar-top"]/div[1]/div[5]/button')
            ActionChains(self.__browser).move_to_element(b).perform()
            b.click()
            # print('Балансування')
            r = self.to_check_ready(By.XPATH, '/html/body/div[2]/div[2]/div/div/div/div/button')
            r.click()
            # print('Результати балансування')
            k = self.to_check_ready(By.XPATH, '/html/body/div[2]/div[3]/div/div/div/span/button[1]')
            ActionChains(self.__browser).move_to_element(k).perform()
            k.click()

            # print('Вибрали меню Компоненти балансування')
            # Переключаємось на iframe що містить дані
            frame = self.to_check_ready(By.CLASS_NAME, 'emfamily-frame')
            self.__browser.switch_to.frame(self.__browser.find_element(By.CLASS_NAME, 'emfamily-frame'))
            print('Переключились на iframe')
            # driver.switch_to.default_content()
        except() as ex:
            print(str(ex))
            logger.error(str(ex))
            self.__browser.close()
            exit("ERROR in open_page_of_components function: No such element. Change structure site OR No connect!!!")

    # period_delta - кількість днів отримана з argparser
    def run_perform(self, today_date, period_delta: int, type_cmp: str, role: str, info_label: str):

        while period_delta >= 0:
            t_day = str((today_date - timedelta(days=period_delta)).strftime('%d'))
            t_month = str((today_date - timedelta(days=period_delta)).strftime('%m'))
            t_year = str((today_date - timedelta(days=period_delta)).year)

            result = False
            num_try = [0, 1, 2] # робимо 3 спроби, якщо сторінка не завантажується
            for x in num_try:
                result = self.load_component(
                    c_day=t_day, c_month=t_month, c_year=t_year, type_cmp=type_cmp, role=role, info=info_label)
                if result:
                    break
                else:
                    # оновлюємо сторінку, вибираємо компоненти балансування та переходимо на наступну ітерацію цикла
                    self.open_page_of_components()
            if not result:  # три спроби невдалі
                exit(f'Не вдалось завантажити сторінку із 3-х спроб.')
            period_delta -= 1

    def load_component(self, c_day: str, c_month: str, c_year: str, type_cmp: str, role: str,
                       info: str):  # version: str,
        print(info)
        print(f'Вибір даних за: {c_day}.{c_month}.{c_year} тип компонента: {type_cmp} ')  # версія: {version}
        logger.info(f'Вибір даних за: {c_day}.{c_month}.{c_year}')
        try:
            # self.__browser.find_element(By.CLASS_NAME, "ААААААbackButton").click()
            self.__browser.implicitly_wait(3)
            WebDriverWait(self.__browser, 10).until(
                lambda ddriver: self.__browser.execute_script('return document.readyState') == 'complete'
            )
            # Обираємо параметри формування звіту:
            # Тип компонента балансування
            Select(self.__browser.find_element(By.NAME, "mainBean.componentTypes")).deselect_all()
            sleep(1)
            Select(self.__browser.find_element(By.NAME, "mainBean.componentTypes")).select_by_value(type_cmp)
            print(f'Вибрали тип компонента')
            sleep(1)
            # За тип періоду - День
            # day_value_from_yesterday = str((date.today() - timedelta(days=SCL_TIME_DELTA_DAYS)).day)
            self.__browser.find_element(By.NAME, "dateTypeChooser.dateTypeFilter").click()
            Select(self.__browser.find_element(By.NAME, "dateTypeChooser.dateTypeFilter")).select_by_value('DAY')
            # print('Вибрали тип періоду- День')
            (Select(self.__browser.find_element(By.NAME, "dateTypeChooser.year")).
             select_by_visible_text(c_year))
            # print(f'Вибрали Рік- {c_year}')
            (Select(self.__browser.find_element(By.NAME, "dateTypeChooser.month")).
             select_by_visible_text(c_month))
            # print(f'Вибрали місяць- {c_month}')
            (Select(self.__browser.find_element(By.NAME, "dateTypeChooser.day")).
             select_by_visible_text(c_day))
            # print(f'Вибрали число- {c_day}')
            print(f'Вибрали дату  {c_year}-{c_month}-{c_day}')
            # Обираємо торгову зону 'UA-IPS_MBA'
            # (Select(self.__browser.find_element(By.NAME, "mainBean.functionalGroupPk")).
            #  select_by_visible_text('UA-IPS_MBA'))
            # print('Вибрали торгову зону UA-IPS_MBA')
            # Натискаємо кнопку "пошук"
            self.__browser.find_element(By.ID, "filterButton").click()
            print('Клікнули Пошук')
            WebDriverWait(self.__browser, 10).until(
                lambda ddriver: self.__browser.execute_script('return document.readyState') == 'complete'
            )
            self.__browser.implicitly_wait(5)
            # print('функція readystate = complete відпрацювала')
            list_contetnt_div = self.to_check_ready(By.CLASS_NAME, 'listContentDiv')
            # print('функція to_check_ready відпрацювала')

            # тут вибиває exception
            html_doc = self.__browser.page_source
            soup = BeautifulSoup(html_doc, 'html.parser')
            table = soup.find(class_="listContentDiv")

            # функція перевіряє існування компоненту по UID. Якщо не існує, то перевіряємо існування ОЕР1 та ОЕР2 -
            # створюємо оери та новий компонент. Потім вручну потрібно буде прив'язати ОЕР до компанії
            # (таблиця ms_dict_companies) щоб могли формувати звіт в розрізі компаній

            check_result = APP().check_component(table)
            if check_result:  # перелік компонентів на сайті непустий

                # Чекбоксом обираємо усі рядки
                self.__browser.find_element(By.CSS_SELECTOR,
                                            "#listTableHeader>td:nth-child(12)>nobr>input[type=CHECKBOX]").click()
                print('Встановили чекбокси')
                self.__browser.find_element(By.NAME, "mainBean.version").click()
                # Select(self.__browser.find_element(By.NAME, "mainBean.version")).select_by_value(version)
                seloption = Select(self.__browser.find_element(By.NAME, "mainBean.version")).first_selected_option
                if seloption.text == '*':
                    print('Версії вимірів 1, 2, 3')
                else:
                    logger.error(f'Невірне значення поля версії {seloption.text}')
                    exit(f'Невірне значення поля версії {seloption.text}')
                # print(f'Вибрали версію- {version}')
                # Натискаємо кнопку Показати часові ряди
                self.__browser.find_element(By.CSS_SELECTOR,
                                            "body>div>div>form>div:nth-child(24)>nobr>input:nth-child(4)").click()
                print('Клікнули Показати часові ряди')
                self.__browser.implicitly_wait(7)
                # sleep(5)
                # WebDriverWait(self.__browser, 10).until(
                #     lambda ddriver: self.__browser.execute_script('return document.readyState') == 'complete'
                # )
                # print('функція document.readyState == complete відпрацювала')
                # перевіримо чи завантажилась таблиця часових рядів
                hours_table = self.to_check_ready(By.ID, 'tsOuterTable')
                html_doc = self.__browser.page_source
                soup = BeautifulSoup(html_doc, 'html.parser')
                # sleep(5)
                ts_outer_table = soup.find("table", id="tsOuterTable")
                ts_header_tko_table = soup.find("div", id="scrollHeader")
                ts_header_tko_table = ts_header_tko_table.table.tbody
                ts_header_tko = ts_header_tko_table.find("tr")

                # Take names of tko from title attribute in table headers
                tko_name_lst = [td['title'] for td in ts_header_tko.find_all("td")]
                # зробимо словник, де ключ буде назва компоненту, а значення буде uid компоненту
                tko_uid_dict = {}
                lst_db_components = DB().get_all_components()

                # Перевіримо чи всі назви колонок часових рядів присутні в БД
                db_itko = [db.integrate_tko for db in lst_db_components]
                absent_nam = list(set(tko_name_lst).difference(db_itko))  # які назви колонок час.рядів відсутні в БД?
                if absent_nam:
                    logger.error(f'ПОМИЛКА! В БД не знайдено назву компонента : {absent_nam}')
                    exit(f'ПОМИЛКА! В БД не знайдено назву компонента: {absent_nam}')

                for n in tko_name_lst:  # Знаходимо uid для колонки часових рядів
                    for c in lst_db_components:
                        if c.integrate_tko == n:
                            tko_uid_dict[c.integrate_tko] = c.uid
                            # Перевіримо чи тип компонентy параметру функції співпадає з типом компоненту в БД
                            if c.c_type_name_en != type_cmp:
                                logger.error(
                                    f' Помилка! Тип компонентy в параметрах функції {type_cmp} не співпадає з типом '
                                    f'компоненту в БД {c.c_type_name_en}')
                                exit(f' Помилка! Тип компонентy в параметрах функції {type_cmp} не співпадає з типом '
                                     f'компоненту в БД {c.c_type_name_en}')
                            break

                print('Готуємо таблицю значень до збереження в БД')  # підготовка даних для збереження в БД
                lst_insert = APP().prepare_time_values(ts_outer_table, tko_uid_dict)  # version
                if lst_insert:
                    print("Починаємо завантаження в базу даних")
                    lst_result = DB().add_time_values(lst_insert, type_cmp, role)  # додаємо нові часові ряди
                    if lst_result:
                        print(f'Збережено вимірів: {lst_result}'  # версія: {version}
                              f'\n---------------------------')
                        logger.info(f'Збережено вимірів: {lst_result}')  # версія: {version}
                        self.__browser.find_element(By.CLASS_NAME, "backButton").click()
                        print('Натиснули кнопку Назад')
                        return True
                    else:
                        print("Пустий список, нічого не зберегли")
                        self.__browser.find_element(By.CLASS_NAME, "backButton").click()
                        print('Натиснули кнопку Назад')
                        return True

            else:
                print('---------------------------')
                return True
        except (NoSuchElementException, WebDriverException):

            print("Помилка завантаження сторінки ! Ще одна спроба....")
            logger.error("Помилка завантаження сторінки ! Ще одна спроба....")
            return False

    def close(self):
        try:
            if self.__browser:
                self.__browser.close()
        except (MaxRetryError, InvalidSessionIdException) as ex:
            logger.error(str(ex))
            print(str(ex))

    def request_imbalance(self, start_date, end_date, url_imb_page):

        url = f'{url_imb_page}&periodFrom={start_date}&periodTo={end_date}'
        try:
            self.__browser.get(url)
            WebDriverWait(self.__browser, 10).until(
                lambda ddriver: self.__browser.execute_script('return document.readyState') == 'complete'
            )
            html_doc = self.__browser.page_source
            soup = BeautifulSoup(html_doc, 'html.parser')
            pre_tag = soup.find('pre')
            json_data = pre_tag.text
            data_list = json.loads(json_data)
            print('Готуємо таблицю небалансів до збереження в БД')
            lst_insert = APP().prepare_imbalance(data_list)
            if lst_insert:
                print(f"Починаємо завантаження небалансів в базу даних з {start_date} по {end_date}")
                lst_result = DB().add_imbalance_values(lst_insert)  # додаємо нові значення розрахунків небалансів
                if lst_result:
                    cnt_ids = len(lst_result)
                    sum_credit = DB().get_credit_imbalance(start_date, end_date)
                    msg = (f'Розрахунок небалансів: додано/оновлено: {cnt_ids} рядків за період з {start_date} '
                           f'по {end_date} Всього кредит: {sum_credit} грн.')
                    print(msg)
                    print('==============================')
                    logger.info(msg)
            else:
                msg = f'Розрахунок небалансів: немає даних за період з {start_date} по {end_date}'
                logger.info(msg)
                print(msg)

        except (NoSuchElementException, WebDriverException) as ex:
            print(str(ex))
            logger.error(str(ex))
            print("ERROR in request_imbalance function: No such element. Change structure site OR No connect!")
