from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, Table, func, between
from sqlalchemy.exc import OperationalError, IntegrityError, DBAPIError
from sqlalchemy.orm import aliased

from appclasses import Contract, Trader, Place, Oblenergo, PersonalAccount, TypeImbalance, User, Company, \
    DbComponent, Account
from config import logger
from database.connection import ConnectionDB
from database.structure import MmsDictTraderContract, MmsDictTrader, MmsGrafValue, MmsDictConsumptionPlace, \
    MmsDictOblenergo, MmsDictPersEnergyAccount, MmsConsumptionValue, MmsImbalance, MmsDictImbalanceType, MmsDictUser, \
    MmsDictCompany, MmsDictUserCompany, MmsDictAccount, MmsDictComponent, MmsDictComponentType, MmsGenerationValue, \
    MmsGrafProdValue, MmsPurchaseValue, MmsDeliveryValue
from sqlalchemy import text
import pandas as pd
import datetime as dt


class DB(ConnectionDB):

    def add_uid_component(self, table_for_add, item):
        # cnn_obj: ConnectionDB = ConnectionDB()
        # # cnn_obj = ConnectionDB()
        try:
            cnn = self.set_connection()
            pea_from = item[list(item.keys())[4]]
            pea_to = item[list(item.keys())[5]]
            sql_from = select(MmsDictTrader.id.label('id_pea_from')).where(MmsDictTrader.pea == pea_from)
            sql_to = select(MmsDictTrader.id.label('id_pea_to')).where(MmsDictTrader.pea == pea_to)
            sql = select(MmsDictTrader.pea)
            db_request_from = cnn.execute(sql)

            list_id = [x.pea for x in db_request_from]
            if pea_from not in list_id and pea_from not in pea_to:
                sql_cmd = (insert(MmsDictTrader).values(pea=pea_from, name=pea_from, active=True)
                           .returning(MmsDictTrader.id, MmsDictTrader.name))
                # sql_cmd = (insert(MmsDictTrader).values(pea=pea_from, name=pea_from, active=True))
                ss = cnn.execute(sql_cmd)
                cnn.commit()
                for x in ss:
                    print(x.id, x.name)
                print('...................................................................')

            # db_request_to = cnn.execute(sql_to)
            print(pea_from, '+++++++++++', pea_to)

            # sql = select(MmsDictTraderContract.uid, MmsDictTraderContract.tko).where(
            #     MmsDictTraderContract.uid.in_(lst_df_uid))

        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція add_uid_component")
            logger.error(str(ex))
            print(str(ex))
        finally:
            self.close_connection()
            print("роботу функції add_uid_component завершено")

    def get_all_contracts(self) -> list[Contract]:
        lst = []
        # cnn_obj: ConnectionDB = ConnectionDB()
        try:
            # cnn = cnn_obj.set_connection()
            cnn = self.set_connection()
            sql = select(MmsDictTraderContract)
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(
                    Contract(
                        uid=x.uid, tko=x.tko, trader_id_from=x.trader_id_from,
                        trader_id_to=x.trader_id_to, valid_from=x.valid_from, valid_to=x.valid_to
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_all_contracts ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            # cnn_obj.close_connection()
            self.close_connection()
        return lst

    def get_all_component_types(self) -> list:
        lst = []
        try:
            cnn = self.set_connection()
            sql = select(MmsDictComponentType)
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(dict(id=x.id, name=x.name, name_en=x.name_en))
                # print(f'{x.id}-----{x.name}---------/////------')
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_all_component_types")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst

    def get_all_components(self) -> list[DbComponent]:
        lst = []
        try:
            acc_from = aliased(MmsDictAccount)
            acc_to = aliased(MmsDictAccount)
            cnn = self.set_connection()
            sql = (select(MmsDictComponent.uid, MmsDictComponent.tko.label('tko'),
                          MmsDictComponent.account_id_from, MmsDictComponent.account_id_to,
                          MmsDictComponent.valid_from, MmsDictComponent.valid_to, MmsDictComponent.component_type_id,
                          MmsDictComponentType.name.label('c_type_name'),
                          MmsDictComponentType.name_en.label('c_type_name_en'),
                          MmsDictComponentType.postfix.label('postfix'),
                          (func.concat(acc_from.nickname, '-', acc_to.nickname, MmsDictComponentType.postfix)).label(
                              'integrate_tko')
                          )
                   .join(acc_from, MmsDictComponent.account_id_from == acc_from.id, isouter=True)
                   .join(acc_to, MmsDictComponent.account_id_to == acc_to.id, isouter=True)
                   .join(MmsDictComponentType, MmsDictComponent.component_type_id == MmsDictComponentType.id,
                         isouter=True)
                   )
            # print(sql)
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(
                    DbComponent(
                        uid=x.uid, tko=x.tko, component_type_id=x.component_type_id, account_id_from=x.account_id_from,
                        account_id_to=x.account_id_to, valid_from=x.valid_from, valid_to=x.valid_to, postfix=x.postfix,
                        integrate_tko=x.integrate_tko, c_type_name=x.c_type_name, c_type_name_en=x.c_type_name_en
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_all_components ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst

    def get_all_accounts(self) -> list[Account]:
        lst = []
        try:
            cnn = self.set_connection()
            sql = (select(MmsDictAccount.id, MmsDictAccount.name, MmsDictAccount.nickname, MmsDictAccount.company_id,
                          MmsDictAccount.active, MmsDictAccount.xcode, MmsDictCompany.name.label('company_name'),
                          MmsDictCompany.nickname.label('company_nickname'))
                   .join(MmsDictCompany, MmsDictAccount.company_id == MmsDictCompany.id,
                         isouter=True)
                   )
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(
                    Account(
                        id_=x.id, name=x.name, nickname=x.nickname, xcode=x.xcode, company_id=x.company_id,
                        company_name=x.company_name, company_nickname=x.company_nickname, active=x.active
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_all_accounts")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst

    def get_types_imbalance(self) -> list[TypeImbalance]:
        lst = []
        try:
            cnn = self.set_connection()
            sql = select(MmsDictImbalanceType)
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(
                    TypeImbalance(
                        id_=x.id, name=x.name, name_transaction=x.name_transaction, name_direction=x.name_direction,
                        name_en_direction=x.name_en_direction
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_types_imbalance")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst

    def get_all_oblenergos(self) -> list[Oblenergo]:
        lst = []
        try:
            cnn = self.set_connection()
            sql = select(MmsDictOblenergo)
            db_request = cnn.execute(sql)
            for x in db_request:
                lst.append(
                    Oblenergo(
                        id_=x.id, name=x.name, pea=x.pea, active=x.active
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_all_oblenergos ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst

    def add_accounts(self, lst_new_accounts) -> list[Account]:
        lst_added = []
        try:
            cnn = self.set_connection()
            sql_cmd = (insert(MmsDictAccount).values(lst_new_accounts)
                       .returning(MmsDictAccount.id, MmsDictAccount.name, MmsDictAccount.nickname,
                                  MmsDictAccount.active)
                       )
            db_request = cnn.execute(sql_cmd)
            cnn.commit()
            for x in db_request:
                lst_added.append(
                    Account(
                        id_=x.id, name=x.name, nickname=x.nickname, active=x.active
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція add_accounts")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst_added

    def add_components(self, lst_new_components) -> list[DbComponent]:
        lst_added = []
        try:
            cnn = self.set_connection()
            sql_cmd = (insert(MmsDictComponent).values(lst_new_components)
                       .returning(MmsDictComponent.uid, MmsDictComponent.tko, MmsDictComponent.account_id_from,
                                  MmsDictComponent.component_type_id, MmsDictComponent.account_id_to,
                                  MmsDictComponent.valid_from, MmsDictComponent.valid_to))
            db_request = cnn.execute(sql_cmd)
            cnn.commit()
            for x in db_request:
                lst_added.append(
                    DbComponent(
                        uid=x.uid, tko=x.tko, account_id_from=x.account_id_from, account_id_to=x.account_id_to,
                        component_type_id=x.component_type_id, valid_from=x.valid_from, valid_to=x.valid_to
                    )
                )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція add_components")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst_added

    def add_time_values(self, lst_values, type_cmp: str, role: str):

        count_uid = 0
        try:

            if type_cmp == 'GENERATION':
                target_table = MmsGenerationValue
            elif type_cmp == 'CONSUMPTION':
                target_table = MmsConsumptionValue
            elif type_cmp == 'SCHEDULE' and role == 'PROD':
                target_table = MmsGrafProdValue
            elif type_cmp == 'SCHEDULE' and role == 'BRP':
                target_table = MmsGrafValue
            elif type_cmp == 'PURCHASE':
                target_table = MmsPurchaseValue
            elif type_cmp == 'DELIVERY':
                target_table = MmsDeliveryValue
            else:
                logger.error(f'Помилка! Невідомий тип компонента {type_cmp} {role}')
                exit(f'Помилка! Невідомий тип компонента {type_cmp} {role}')
            cnn = self.set_connection()
            sql_cmd = (insert(target_table).values(lst_values))
            sql_cmd = (sql_cmd.on_conflict_do_update(
                index_elements=[target_table.component_uid, target_table.version_id, target_table.date_meter,
                                target_table.hour_from, target_table.hour_to],
                set_=dict(value_meter=sql_cmd.excluded.value_meter))
                       .returning(target_table.component_uid))

            db_request = cnn.execute(sql_cmd)
            cnn.commit()
            for x in db_request:
                count_uid += 1
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція add_time_values ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return count_uid

    def add_imbalance_values(self, lst_insert: list):

        list_ids = []
        try:
            cnn = self.set_connection()
            sql_cmd = (insert(MmsImbalance).values(lst_insert))
            sql_cmd = (sql_cmd.on_conflict_do_update(
                index_elements=[MmsImbalance.date_calc, MmsImbalance.hour_from, MmsImbalance.hour_to],
                set_=dict(type_id=sql_cmd.excluded.type_id,
                          imbalance_amount=sql_cmd.excluded.imbalance_amount,
                          imsp_price=sql_cmd.excluded.imsp_price,
                          rdn_price=sql_cmd.excluded.rdn_price,
                          payment_price=sql_cmd.excluded.payment_price,
                          payment_sum=sql_cmd.excluded.payment_sum))
                       .returning(MmsImbalance.id))
            # print(lst_insert)
            db_request = cnn.execute(sql_cmd)
            cnn.commit()
            for x in db_request:
                list_ids.append(x)
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція add_imbalace_values ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
            return list_ids

    def get_credit_imbalance(self, start_date: str, end_date: str):
        lst = []
        try:
            cnn = self.set_connection()
            credit = (
                select(func.sum(MmsImbalance.payment_sum).label('credit'))
                .where(MmsImbalance.date_calc.between(start_date, end_date) &
                       (MmsImbalance.type_id == 2)
                       )
            ).as_scalar()
            debit = (
                select(func.sum(MmsImbalance.payment_sum).label('debit'))
                .where(MmsImbalance.date_calc.between(start_date, end_date) &
                       (MmsImbalance.type_id == 1)
                       )
            ).as_scalar()
            main_sql = (select((credit - debit).label('credit_total')))
            db_request = cnn.execute(main_sql)
            sum_credit_total = db_request.cursor.fetchall()[0][0]

        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_credit_imbalance ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return sum_credit_total

    # Варіант звіту коли співпадіння контрагента шукається по назві, буває що не знаходить (можливо по причині кавичок)
    # переробила на пошук по uid
    def get_report_trading_old(self, dtstart, dtend, direction: str, version: str):

        # engine = cnn_obj.engine
        antidirection = ''
        try:
            # df = pd.read_sql(sq1, engine)
            if direction == 'from':
                antidirection = 'to'

            if direction == 'to':
                antidirection = 'from'
            cnn = self.set_connection()
            sq1 = text(
                "select DISTINCT mdt.name from mms_graf_values gv left join mms_dict_trader_contracts mdtc on "
                f"gv.trader_contract_uid = mdtc.uid left join mms_dict_traders mdt on "
                f"mdtc.trader_id_{antidirection} = mdt.id "
                f"where date_meter between '{dtstart}'::date and '{dtend}'::date and value_meter is not NULL and "
                f"version_id = {version}"
                f"and mdtc.trader_id_{direction} = 1 order by 1"
            )
            results = cnn.execute(sq1)
            list_names = [x.name for x in results]
            if list_names is not None:
                sql_start, sql_middle, sql_end = '', '', ''
                sql_start = text("select gv.date_meter, gv.hour_from, gv.hour_to, ")
                for x in list_names:
                    # print(f'{x}++++++')
                    name_ltd = x
                    name_ltd = name_ltd.replace("'", "''")
                    name_ltd = name_ltd.replace('"', "''")
                    tt = text(
                        f"sum(case when mdt.name = '{name_ltd}' then value_meter else 0 end) as \"{name_ltd}\", "
                    )
                    sql_middle += str(tt)
                sql_end = text(
                    "sum(value_meter) from mms_graf_values gv left join mms_dict_trader_contracts mdtc on "
                    "gv.trader_contract_uid = mdtc.uid  left join mms_dict_traders mdt on "
                    f"mdtc.trader_id_{antidirection} = "
                    f"mdt.id  where date_meter between '{dtstart}'::date and '{dtend}'::date and version_id = {version}"
                    f" and value_meter is not NULL and mdtc.trader_id_{direction} = 1 group by gv.date_meter, "
                    "gv.hour_from, gv.hour_to order by gv.date_meter, gv.hour_from"
                )
                sql_start = str(sql_start)
                sql_middle = str(sql_middle)
                sql_end = str(sql_end)
                sqll = sql_start + sql_middle + sql_end
                # print(sqll)
                sqlf = text(sqll)
                # print(sqlf)
                # results = cnn.execute(sqlf)
                # if results:
                #     # list_names = [x.name for x in results]
                #     for x in results:
                #         print(f'{x}')
                engine = self.engine
                df = pd.read_sql(sqll, engine)
                today = dt.datetime.today().strftime("%Y%m%d")
                now = dt.datetime.now().strftime("%H%M%S")
                df.to_excel(r'REPORTS\schedule_' + today + now + '.xlsx', sheet_name=r'schedule_v' + version + '_' +
                                                                                     direction + ' KNESS_ENERGY')
                return True
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_report_trading")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return False

    def get_report_consumption(self, dtstart, dtend, version: str):

        try:
            # df = pd.read_sql(sq1, engine)
            cnn = self.set_connection()
            # engine = cnn_obj.engine
            sq1 = text(
                "select mdc.uid as uid, mdcof.name as company_from_name, "
                "concat(mdaf.nickname,' - ', mdat.nickname) as cname "
                "from mms_dict_components mdc  "
                "left join mms_dict_accounts mdaf on mdc.account_id_from = mdaf.id "
                "left join mms_dict_accounts mdat on mdc.account_id_to = mdat.id "
                "left join mms_dict_companies mdcof on mdaf.company_id = mdcof.id "
                "left join mms_dict_companies mdcot on mdat.company_id = mdcot.id "
                f"where mdat.company_id = 1 and mdc.account_id_to in (3, 4) "
                f"order by array_position(array['MGA-00100', 'MGA-01600', 'MGA-00400', "
                f"'MGA-00900', 'MGA-01800', 'MGA-00200', 'MGA-00800', 'MGA-01000', 'MGA-01100', 'MGA-01200', "
                f"'MGA-01400', 'MGA-01500', 'MGA-01900', 'MGA-02100', 'MGA-02200', 'MGA-02400', 'MGA-02800', "
                f"'MGA-02900', 'MGA-03000', 'MGA-00000'],mdaf.nickname), mdc.account_id_to"
            )
            # print(sq1)
            results = cnn.execute(sq1)
            list_uids, list_addname = [], []
            for x in results:
                xdict = {x.uid: x.cname}
                list_uids.append(xdict)
                list_addname.append(f'{x.company_from_name}  ')  # MGA-********* {x.uid} -
            list_addname.append('+')
            if list_uids is not None:
                sql_start, sql_middle, sql_end = '', '', ''
                sql_start = text("select mcv.date_meter, mcv.hour_from, mcv.hour_to, ")
                for xx in list_uids:
                    for uid, val in xx.items():
                        name_ltd = val
                        name_ltd = name_ltd.replace("'", "''")
                        name_ltd = name_ltd.replace('"', "''")
                        tt = text(
                            f"sum(case when mcv.component_uid = {uid} then value_meter else 0 end) "
                            f"as \"{name_ltd}\", "
                        )
                        sql_middle += str(tt)
                sql_end = text(
                    f"sum(value_meter) from mms_consumption_values mcv where mcv.date_meter between '{dtstart}'::date and "
                    f"'{dtend}'::date and mcv.value_meter is not null and mcv.version_id = {version} group by "
                    "mcv.date_meter, mcv.hour_from, mcv.hour_to order by mcv.date_meter, mcv.hour_from"
                )
                sql_start = str(sql_start)
                sql_middle = str(sql_middle)
                sql_end = str(sql_end)
                sqll = sql_start + sql_middle + sql_end
                # print(sqll)
                engine = self.engine
                df = pd.read_sql(sqll, engine)
                i, j = 0, 0
                for column in df:
                    namc = df[column].name
                    if i > 2:
                        df.rename(columns={namc: f"{list_addname[j]} {namc}"}, inplace=True)
                        j += 1
                    i += 1
                today = dt.datetime.today().strftime("%Y%m%d")
                now = dt.datetime.now().strftime("%H%M%S")
                df.to_excel(r'REPORTS\consumption_' + today + now + '.xlsx', sheet_name=r'consumption_v' + version)
                return True
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_report_consumption")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return False

    def get_report_trading(self, dtstart, dtend, direction: str, version: str):

        antidirection = ''
        try:
            # df = pd.read_sql(sq1, engine)
            if direction == 'from':
                antidirection = 'to'

            if direction == 'to':
                antidirection = 'from'
            cnn = self.set_connection()

            sq1 = text(
                "select DISTINCT gv.component_uid as uid, coalesce(mdco.name, 'невизначено') as company_name, "
                "concat(' - ',mda.nickname) as acc_nickname "
                "from mms_graf_values gv "
                "left join mms_dict_components mdc on gv.component_uid = mdc.uid "
                f"left join mms_dict_accounts mda on mdc.account_id_{antidirection} = mda.id "
                f"left join mms_dict_companies mdco on mda.company_id = mdco.id "
                f"where date_meter between '{dtstart}'::date and '{dtend}'::date and value_meter is not NULL and "
                f"version_id = {version} "
                f"and mdc.account_id_{direction} = 1 order by 1"
            )
            # print(sq1)
            results = cnn.execute(sq1)
            list_uids, list_addname = [], []
            for x in results:
                xdict = {x.uid: x.acc_nickname}
                list_uids.append(xdict)
                list_addname.append(f'{x.company_name} ')
            list_addname.append('+')
            if list_uids is not None:
                sql_start, sql_middle, sql_end = '', '', ''
                sql_start = text("select gv.date_meter, gv.hour_from, gv.hour_to, ")
                for xx in list_uids:
                    for uid, val in xx.items():
                        name_ltd = val
                        name_ltd = name_ltd.replace("'", "''")
                        name_ltd = name_ltd.replace('"', "''")
                        tt = text(
                            f"sum(case when gv.component_uid = {uid} then value_meter else 0 end) "
                            f"as \"{name_ltd}\", "
                        )
                        sql_middle += str(tt)
                sql_end = text(
                    "sum(value_meter) from mms_graf_values gv left join mms_dict_components mdc on "
                    "gv.component_uid = mdc.uid  left join mms_dict_accounts mda on "
                    f"mdc.account_id_{antidirection} = "
                    f"mda.id  where date_meter between '{dtstart}'::date and '{dtend}'::date and version_id = {version}"
                    f" and value_meter is not NULL and mdc.account_id_{direction} = 1 group by gv.date_meter, "
                    "gv.hour_from, gv.hour_to order by gv.date_meter, gv.hour_from"
                )
                sql_start = str(sql_start)
                sql_middle = str(sql_middle)
                sql_end = str(sql_end)
                sqll = sql_start + sql_middle + sql_end
                # print(sqll)
                sqlf = text(sqll)
                # print(sqlf)
                # results = cnn.execute(sqlf)
                # if results:
                #     # list_names = [x.name for x in results]
                #     for x in results:
                #         print(f'{x}')
                engine = self.engine
                df = pd.read_sql(sqll, engine)
                i, j = 0, 0
                for column in df:
                    namc = df[column].name
                    if i > 2:
                        df.rename(columns={namc: f"{list_addname[j]} {namc}"}, inplace=True)
                        j += 1
                    i += 1
                today = dt.datetime.today().strftime("%Y%m%d")
                now = dt.datetime.now().strftime("%H%M%S")
                df.to_excel(r'REPORTS\schedule_' + today + now + '.xlsx', sheet_name=r'schedule_v' + version + '_' +
                                                                                     direction + ' KNESS_ENERGY')
                return True
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_report_trading")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return False

    def get_info_users(self, lst_logins) -> list[User]:

        lst_users, lst_his_company = [], []
        try:
            cnn = self.set_connection()
            sql = select(MmsDictUser).where(
                (MmsDictUser.login.in_(lst_logins)) & MmsDictUser.active).order_by(MmsDictUser.id.desc())
            # print(f'{sql}+++++++++++++++++++++++++++++++++++++++++')
            db_request = cnn.execute(sql)
            for x in db_request:
                csql = (select(MmsDictUserCompany.company_id, MmsDictCompany.id, MmsDictCompany.name,
                               MmsDictCompany.nickname, MmsDictCompany.xcode, MmsDictCompany.active)
                        .join(MmsDictCompany, MmsDictUserCompany.company_id == MmsDictCompany.id,
                              isouter=True).where((MmsDictUserCompany.user_id == x.id) & MmsDictCompany.active)
                        )
                # print(csql)
                cdb_request = cnn.execute(csql)
                lst_his_company = []
                for cmp in cdb_request:
                    lst_his_company.append(Company(id_=cmp.id, name=cmp.name, nickname=cmp.nickname, xcode=cmp.xcode,
                                                   active=cmp.active
                                                   )
                                           )
                lst_users.append(User(id_=x.id, name=x.name, login=x.login, password=x.password, active=x.active,
                                      companies=lst_his_company
                                      )
                                 )
        except (OperationalError, IntegrityError, DBAPIError) as ex:
            print("Помилка бази даних. Функція get_info_users ")
            logger.error(str(ex))
            exit(str(ex))
        finally:
            self.close_connection()
        return lst_users
