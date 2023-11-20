from datetime import date


# клас таблиці сайту Компоненти балансування
class SiteComponent:
    def __init__(
            self, uid: int, tko: str, type_c: str, pea_from: str, pea_to: str, valid_from: date, valid_to: date
    ):
        self.uid: int = uid
        self.tko: str = tko
        self.type_c: str = type_c
        self.pea_from: str = pea_from
        self.pea_to: str = pea_to
        self.valid_from: date = valid_from
        self.valid_to: date = valid_to


class DbComponent:
    def __init__(
            self, uid: int, tko: str, component_type_id: int, account_id_from: int, account_id_to: int,
            valid_from: date, valid_to: date, postfix: str | None = None, integrate_tko: str | None = None, c_type_name: str | None = None, c_type_name_en: str | None = None
    ):
        self.uid: int = uid
        self.tko: str = tko
        self.component_type_id: int = component_type_id
        self.account_id_from: int = account_id_from
        self.account_id_to: int = account_id_to
        self.valid_from: date = valid_from
        self.valid_to: date = valid_to
        self.postfix: str | None = postfix
        self.integrate_tko: str | None = integrate_tko
        self.c_type_name: str | None = c_type_name
        self.c_type_name_en: str | None = c_type_name_en



# клас таблиці mms_dict_trader_contracts
class Contract:
    def __init__(
            self, uid: int, tko: str, trader_id_from: int, trader_id_to: int, valid_from: date, valid_to: date
    ):
        self.uid: int = uid
        self.tko: str = tko
        self.trader_id_from: int = trader_id_from
        self.trader_id_to: int = trader_id_to
        self.valid_from: date = valid_from
        self.valid_to: date = valid_to


# клас таблиці mms_dict_traders
class Trader:
    def __init__(
            self, pea: str, active: bool, id_: int | None = None, name: str | None = None
    ):
        self.id_: int | None = id_
        self.name: str | None = name
        self.pea: str = pea
        self.active: bool = active


# клас таблиці mms_dict_oblenergos
class Oblenergo:
    def __init__(
            self, pea: str, active: bool, id_: int | None = None, name: str | None = None
    ):
        self.id_: int | None = id_
        self.name: str | None = name
        self.pea: str = pea
        self.active: bool = active


# клас таблиці mms_dict_pers_energy_accounts
class PersonalAccount:
    def __init__(
            self, name: str, id_: int | None = None
    ):
        self.id_: int | None = id_
        self.name: str = name


# клас таблиці mms_dict_consumption_places
class Place:
    def __init__(
            self, uid: int, tko: str, oblenergo_id_from: int, pers_energy_account_id_to: int, valid_from: date,
            valid_to: date, tko_original: str | None = None
    ):
        self.uid: int = uid
        self.tko: str = tko
        self.tko_original: str | None = tko_original
        self.oblenergo_id_from: int = oblenergo_id_from
        self.pers_energy_account_id_to: int = pers_energy_account_id_to
        self.valid_from: date = valid_from
        self.valid_to: date = valid_to


# клас таблиці mms_graf_values
class GrafValue:
    def __init__(
            self, component_uid: int, version_id: int, date_meter: date, hour_from: int, hour_to: int,
            value_meter: float, id_: int | None = None, tko: str | None = None
    ):
        self.id_: int | None = id_
        self.trader_contract_uid: int = component_uid
        self.version_id: int = version_id
        self.date_meter: date = date_meter
        self.hour_from: int = hour_from
        self.hour_to: int = hour_to
        self.value_meter: float = value_meter
        self.tko: str = tko


class TypeImbalance:
    def __init__(
            self, name: str, name_direction: str, name_transaction: str,
            name_en_direction: str, id_: int | None = None
    ):
        self.id_: int | None = id_
        self.name: str = name
        self.name_direction: str = name_direction
        self.name_transaction: str = name_transaction
        self.name_en_direction: str = name_en_direction


# клас таблиці mms_dict_companies
class Company:
    def __init__(
            self, name: str, nickname: str, xcode: str,
            active: bool, id_: int | None = None
    ):
        self.id_: int | None = id_
        self.name: str = name
        self.nickname: str = nickname
        self.xcode: str = xcode
        self.active: bool = active


# клас таблиці mms_dict_accounts
class Account:
    def __init__(
            self, nickname: str, active: bool, id_: int | None = None, name: str | None = None,
            xcode: str | None = None, company_id: int | None = None, company_name: str | None = None,
            company_nickname: str | None = None
    ):
        self.id_: int | None = id_
        self.name: str | None = name
        self.xcode: str | None = xcode
        self.company_id: int | None = company_id
        self.company_name: str | None = company_name
        self.company_nickname: str | None = company_nickname
        self.nickname: str = nickname
        self.active: bool = active


# клас таблиці mms_dict_users
class User:
    def __init__(
            self, name: str, login: str, password: str,
            active: bool, id_: int | None = None, companies: list[Company] = None
    ):
        self.id_: int | None = id_

        self.name: str = name
        self.login: str = login
        self.password: str = password
        self.active: bool = active
        if companies is None:
            self.companies = []
        else:
            self.companies = companies
