from sqlalchemy import text

from appfunctions import APP
from config import USE_SSH, SSH_HOST
from database.db_functions import DB

if USE_SSH == 1 and SSH_HOST == '185.168.129.104':
    print("--- ONLINE server ---")
elif USE_SSH == 1 and SSH_HOST == '46.164.150.162':
    print("--- TEST server ---")
else:
    print("--- UNKNOWN server ---")

# results = DB().get_report_consumption('2023-09-01', '2023-09-30',  '1')
# results = DB().get_report_consumption('2023-09-01', '2023-09-30',  '1')
# if results:
#     print('ТЕСТ Звіт (споживання) збережено')
# else:
#     print('Помилка збереження звіту (споживання)')

args = APP().report_argparser()  # отримуємо параметри, встановлені користувачем при запуску

if args.reptype == 'schedule':
    # results = DB().get_report_trading('2023-11-01', '2023-11-33', 'from', '1')
    results = DB().get_report_trading(args.fromdate, args.todate, args.direction, args.version)
    if results:
        print('Звіт (графік) збережено')
    else:
        print('Помилка збереження звіту (графік)')

if args.reptype == 'consumption':
    # results = DB().get_report_trading('2023-11-01', '2023-11-33', 'from', '1')
    results = DB().get_report_consumption(args.fromdate, args.todate, args.version)
    if results:
        print('Звіт (споживання) збережено')
    else:
        print('Помилка збереження звіту (споживання)')




