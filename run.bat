@echo off
cd C:\Users\Боднар_ВА\PycharmProjects\mms\venv\Scripts
source activate
cd..
cd..
@echo %1
@echo %2
@echo %3
py main.py %1 %2 %3 %4 %5 %6
pause 
