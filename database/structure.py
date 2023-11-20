from datetime import datetime, date

from sqlalchemy import String, create_engine, MetaData, Boolean, Integer, ForeignKey, DateTime, BigInteger, Float, \
    UniqueConstraint, Date, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from decimal import Decimal
from typing_extensions import Annotated
from sqlalchemy.orm import registry

# engine = create_engine("postgresql+psycopg2://consumer:vW2ho4SlQ92x@127.0.0.1:54321/energy", echo=True)
# metadata_obj = MetaData()

num_6_4 = Annotated[Decimal, 6]
num_12_2 = Annotated[Decimal, 12]
num_6_2 = Annotated[Decimal, 6]


class Base(DeclarativeBase):
    # metadata = metadata_obj
    registry = registry(
        type_annotation_map={
            num_6_4: Numeric(6, 4),
            num_12_2: Numeric(12, 2),
            num_6_2: Numeric(6, 2),
        }
    )


class MmsDictTrader(Base):
    __tablename__ = 'mms_dict_traders'
    __table_args__ = {'comment': 'Довідник контрагентів з трейдингу'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True, unique=False, comment='Назва контрагента')
    pea: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Особовий енергетичний рахунок')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='Активний/неактивний')


# class MmsTest(Base):
#     __tablename__ = 'mms_test'
#     __table_args__ = {'comment': 'TEST'}
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name_test: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='ttt')
#     trader_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_traders.id"))


class MmsDictOblenergo(Base):
    __tablename__ = 'mms_dict_oblenergos'
    __table_args__ = {'comment': 'Довідник контрагентів Обленерго зі споживання ('}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True, unique=True, comment='Назва контрагента')
    pea: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Особовий енергетичний рахунок')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='Активний/неактивний')


class MmsDictTraderContract(Base):
    __tablename__ = 'mms_dict_trader_contracts'
    __table_args__ = {'comment': 'Довідник договорів з трейдерами'}

    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, comment='Ідентифікатор компоненту з сайту')
    tko: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='Кодова назва договору обліку')
    trader_id_from: Mapped[int] = mapped_column(ForeignKey('mms_dict_traders.id'), nullable=False,
                                                comment='Трейдер, який продає')
    trader_id_to: Mapped[int] = mapped_column(ForeignKey('mms_dict_traders.id'), nullable=False,
                                              comment='Трейдер, який купує')
    valid_from: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний з')
    valid_to: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний до')


class MmsDictPersEnergyAccount(Base):
    __tablename__ = 'mms_dict_pers_energy_accounts'
    __table_args__ = {'comment': 'Довідник особових енергетичних рахунків НЕСС'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Назва особового енергетичного'
                                                                                       ' рахунку')


class MmsDictConsumptionPlace(Base):
    __tablename__ = 'mms_dict_consumption_places'
    __table_args__ = {'comment': 'Довідник майданчиків споживання'}

    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, comment='Ідентифікатор компоненту з сайту')
    tko: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='Кодова майданчику обліку '
                                                                                       'споживання')
    oblenergo_id_from: Mapped[int] = mapped_column(ForeignKey('mms_dict_oblenergos.id'), nullable=False,
                                                   comment='Код обленерго')
    pers_energy_account_id_to: Mapped[int] = mapped_column(ForeignKey('mms_dict_pers_energy_accounts.id'),
                                                           nullable=False,
                                                           comment='Особовий енергетичний рахунок НЕСС по споживанню')
    valid_from: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний з')
    valid_to: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний до')


class MmsDictVersion(Base):
    __tablename__ = 'mms_dict_versions'
    __table_args__ = {'comment': 'Довідник версій вимірів'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Назва версії')


class MmsGrafValue(Base):
    __tablename__ = 'mms_graf_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу графік'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_components.uid"),
                                                     nullable=False, comment='Код договору, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')


class MmsConsumptionValue(Base):
    __tablename__ = 'mms_consumption_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу споживання'},
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_dict_components.uid"),
                                               nullable=False, comment='Код компоненту, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')


class MmsDictImbalanceType(Base):
    __tablename__ = 'mms_dict_imbalance_type'
    __table_args__ = {
        'comment': 'Довідник типів небалансу. Складається з двох типів, кожен з яких має декілька назв'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Основна назва')
    name_direction: Mapped[str] = mapped_column(String(50), nullable=False, unique=True,
                                                comment='Назва за напрямком')
    name_transaction: Mapped[str] = mapped_column(String(50), nullable=False, unique=True,
                                                  comment='Назва згідно типу '
                                                          'транзакції')
    name_en_direction: Mapped[str] = mapped_column(String(50), nullable=False, unique=True,
                                                   comment='Назва за напрямком'
                                                           ' англійською')


class MmsImbalance(Base):
    __tablename__ = 'mms_imbalance_values'
    __table_args__ = (
        UniqueConstraint('date_calc', 'hour_from', 'hour_to'),
        {'comment': 'Деталі розрахунків по небалансу електричної енергії'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_imbalance_type.id"),
                                         nullable=False, comment='Тип небалансу')
    date_calc: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата розрахунку небалансу')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Розрахункувий період години з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Розрахункувий період години по')
    imbalance_amount: Mapped[num_6_4] = mapped_column(Numeric, nullable=False, comment='Кількість небалансу МВт*Год')
    imsp_price: Mapped[num_12_2] = mapped_column(Numeric, nullable=False, comment='Фактична ціна IMSP, грн/МВт*Год')
    rdn_price: Mapped[num_12_2] = mapped_column(Numeric, nullable=True, comment='Ціна РДН, грн/МВт*Год')
    payment_price: Mapped[num_12_2] = mapped_column(Numeric, nullable=False, comment='Ціна платежу, грн/МВт*Год')
    payment_sum: Mapped[num_12_2] = mapped_column(Numeric, nullable=False, comment='Сума платежу, грн/МВт*Год')


# ------Друга частина-------------------------------------------------------------------------------------------------

class MmsDictUser(Base):
    __tablename__ = 'mms_dict_users'
    __table_args__ = {'comment': 'Довідник користувачів платформи mms'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True, unique=False, comment='Ім"я користувача')
    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Логін')
    password: Mapped[str] = mapped_column(String(50), nullable=False, unique=False, comment='Пароль')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='Активний/неактивний')


class MmsDictCompany(Base):
    __tablename__ = 'mms_dict_companies'
    __table_args__ = {'comment': 'Довідник компаній'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True, unique=True, comment='Назва компанії')
    nickname: Mapped[str] = mapped_column(String(150), nullable=False, unique=True,
                                          comment='Псевдонім на платформі mms')
    xcode: Mapped[str] = mapped_column(String(50), nullable=True, unique=True, comment='Х-код на платформі mms')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='Активний/неактивний')


class MmsDictUserCompany(Base):
    __tablename__ = 'mms_dict_user_company'
    __table_args__ = {'comment': 'Довідник приналежності користувачів до компаній'}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_users.id"),
                                         nullable=False, comment='Ідентифікатор користувача')
    company_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_companies.id"),
                                            nullable=False, comment='Ідентифікатор компанії')


class MmsDictAccount(Base):
    __tablename__ = 'mms_dict_accounts'
    __table_args__ = {'comment': 'Довідник особових енергетичних рахунків (ОЕР)'}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True, unique=True, comment='Назва ОЕР')
    nickname: Mapped[str] = mapped_column(String(150), nullable=False, unique=True,
                                          comment='Кодова назва ОЕР')
    company_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_companies.id"),
                                            nullable=True, comment='Ідентифікатор приналежності рахунку до компанії')
    xcode: Mapped[str] = mapped_column(String(50), nullable=True, unique=True, comment='Х-код на платформі mms')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='Активний/неактивний')


class MmsDictComponentType(Base):
    __tablename__ = 'mms_dict_component_type'
    __table_args__ = {'comment': 'Довідник типів компонентів'}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Назва')
    name_en: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Назва англ.')
    postfix: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='Постфікс для складеної '
                                                                                          'назви тко')


class MmsDictComponent(Base):
    __tablename__ = 'mms_dict_components'
    __table_args__ = {'comment': 'Довідник компонентів балансування'}

    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, comment='Ідентифікатор компоненту з сайту')
    tko: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, comment='Кодова назва з сайту')
    account_id_from: Mapped[int] = mapped_column(ForeignKey('mms_dict_accounts.id'), nullable=False,
                                                 comment='ОЕР звідки поступає електроенергія')
    account_id_to: Mapped[int] = mapped_column(ForeignKey('mms_dict_accounts.id'), nullable=False,
                                               comment='ОЕР куди поступає електроенергія')
    component_type_id: Mapped[int] = mapped_column(ForeignKey('mms_dict_component_type.id'), nullable=False,
                                                   comment='Тип компонента')
    valid_from: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний з')
    valid_to: Mapped[date] = mapped_column(Date, nullable=True, comment='Дійсний до')


class MmsGenerationValue(Base):
    __tablename__ = 'mms_generation_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу Генерація'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_dict_components.uid"),
                                               nullable=False, comment='Код компоненту, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')


class MmsGrafProdValue(Base):
    __tablename__ = 'mms_graf_prod_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу Гафік для ролі PROD'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_dict_components.uid"),
                                               nullable=False, comment='Код компоненту, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')


class MmsDeliveryValue(Base):
    __tablename__ = 'mms_delivery_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу Доставка'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_dict_components.uid"),
                                               nullable=False, comment='Код компоненту, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')


class MmsPurchaseValue(Base):
    __tablename__ = 'mms_purchase_values'
    __table_args__ = (
        UniqueConstraint('component_uid', 'date_meter', 'version_id', 'hour_from', 'hour_to'),
        {"comment": 'Виміри типу Покупка'},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    component_uid: Mapped[int] = mapped_column(ForeignKey("mms_dict_components.uid"),
                                               nullable=False, comment='Код компоненту, до якого відноситься вимір')
    version_id: Mapped[int] = mapped_column(ForeignKey("mms_dict_versions.id"), nullable=False,
                                            comment='Код версії виміру')
    date_meter: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата виміру')
    hour_from: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру з')
    hour_to: Mapped[int(1)] = mapped_column(Integer, nullable=False, comment='Години виміру по')
    value_meter: Mapped[float] = mapped_column(Float, nullable=True, comment='Значення виміру кВтГод')
