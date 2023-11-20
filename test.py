# from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions
#
# my_element_id = 'something123'
# ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
# your_element = WebDriverWait(your_driver, some_timeout,ignored_exceptions=ignored_exceptions)\
#                         .until(expected_conditions.presence_of_element_located((By.ID, my_element_id)))

from datetime import date, timedelta
tod = date.today()
imb_delta = 7
start_date = (tod-timedelta(days=imb_delta)).strftime("%d.%m.%Y")
end_date = tod.strftime("%d.%m.%Y")
print(start_date)
print(end_date)
tod = date.today().strftime("%#d")
print (f'{tod}+++++++++++++++++++++')
current_month = str((date.today() - timedelta(days=2)).strftime('%m'))
mmm = (date.today() - timedelta(days=2)).strftime('%m')
trg_date = str((date.today() - timedelta(days=1395)))

print(trg_date)


d0 = date(2022, 3, 22)
d1 = date(2023, 10, 28)
delta = d1 - d0
print('The number of days between the given range of dates is :')
print(delta.days)

lst_insert = []
lst_insert.append(dict(consumption_place_uid=222, version_id=2,
                  date_meter='2023-09-02', hour_from=22, hour_to=23,
                                           value_meter=1212))
lst_insert.append(dict(consumption_place_uid=333, version_id=2,
                  date_meter='2023-09-02', hour_from=23, hour_to=24,
                                           value_meter=2323))
print(lst_insert)






#dt.strftime('%m')
# lst = ['fffdog', 'hhhh', 'ppppppdog', 'rrrdogrrr']
#
# # Iterate through the list and modify elements ending with 'dog'
# modified_lst = [item[:-3] + '.dog' if item.endswith('dog') else item for item in lst]
#
# print(modified_lst)


# # Create the pandas DataFrame
# df = pandas.DataFrame(data, columns=['Name', 'Age'])
#
# df.replace(to_replace='f', value=None, inplace=True)  # '"F@'
#
# # print dataframe.
# print (df)




# list1 = [1133829, 1232231, 1241591, 1241647, 1257187, 1257199, 1269417, 1273033, 1286291, 1305379, 1305389]
# # list2 = [1133829, 1241647, 1305379, 1305389]
# list2 = [1241591, 1241647, 1257187, 1257199, 1269417, 1273033, 1133829, 1232231,  1286291, 1305379, 1305389]
#
# set1 = set(list1)
# set2 = set(list2)
#
# elements_not_in_list2 = set1 - set2
# print(list(elements_not_in_list2))





