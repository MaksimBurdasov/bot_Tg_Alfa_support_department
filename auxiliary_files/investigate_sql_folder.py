import os

print(type(os.listdir(r'C:\Users\U_M1GT7\SHELTER\Python_task(OSSKTB-1544)_tgbot\sql_queries')))

for f in os.listdir(r'C:\Users\U_M1GT7\SHELTER\Python_task(OSSKTB-1544)_tgbot\sql_queries'):
    print(f, type(f))