from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
import sys
import pandas as pd
import numpy as np
import datetime
import time
import os

''' 
TODO: 
Make an executable with args e.g. Myexe.exe -u nick -p 123456 —enddate 2020-05-05
Let users define start and end dates
'''
now = datetime.datetime.now()

newfilename = now.strftime("%Y-%m-%d_%H.%M.%S") + 'SubmittedReport'

try: 
    os.rename(r'Submitted+Reports.csv', newfilename)
except:
    pass

def get_salt_data(user:str ,pwd:str) -> None:
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get("https://www.cnphi-rcrsp.ca/cnphi/faces/login.xhtml?lang=en&jftfdi=&jffi=%2Flogin.xhtml")
    username = driver.find_element_by_id("inputUserName") 
    username.send_keys(user)
    password = driver.find_element_by_id("inputUserPassword") 
    password.send_keys(pwd)

    password.submit() 

    driver.get("https://www.cnphi-rcrsp.ca/salt/listings/listings.xhtml")
    driver.find_element_by_link_text("Export to csv").click()

if __name__ == "__main__":
    user = sys.argv[1]
    pwd = sys.argv[2]
    get_salt_data(user, pwd)

time.sleep(5)

# Data to be transformed
df = pd.read_csv('Submitted+Reports.csv', encoding='latin-1')

# Final table to be filled in with transformed data
df_fin = pd.DataFrame()

# Temp table for manipulating
df_tmp = df.groupby('Jurisdiction')['Report Date'].min().reset_index()

# List of PTs
pts = df_tmp['Jurisdiction'].tolist()


# Transformed data uses full PT name to match order of submitted report:
# ie. Northwest Territories precedes Nova Scotia, but NS precedes NT


# Column 0: PT + Total
df_fin['PT'] = pts

Total = {'PT':'Total'}

df_fin = df_fin.append(Total, ignore_index=True)


# Column 1: PatientTestedCount
df_tmp = df.groupby('Jurisdiction')['Patients Tested'].max().to_frame(name = 'PatientTestedCount').reset_index()

col1 = df_tmp['PatientTestedCount'].tolist()
col1.append(sum(col1))

df_fin['PatientTestedCount'] = col1


# Column 2: ConfirmedPositiveCount
df_tmp = df.groupby('Jurisdiction')['Confirmed Positive'].max().to_frame(name = 'ConfirmedPositiveCount').reset_index()

col2 = df_tmp['ConfirmedPositiveCount'].tolist()
col2.append(sum(col2))

df_fin['ConfirmedPositiveCount'] = col2


# Column 3: ConfirmedNegativeCount
df_tmp = df.groupby('Jurisdiction')['Confirmed Negative'].max().to_frame(name = 'ConfirmedNegativeCount').reset_index()

col3 = df_tmp['ConfirmedNegativeCount'].tolist()
col3.append(sum(col3))

df_fin['ConfirmedNegativeCount'] = col3


# Column 4: PatientTestedCountChange
col4 = []

for pt in pts:
    df_tmp = df.sort_values(['Jurisdiction', 'Patients Tested'], ascending=[True, False])
    df_tmp.set_index('Jurisdiction', inplace=True)
    df_tmp = df_tmp.loc[[pt], ['Patients Tested']]
    df_tmp = df_tmp.iloc[0] - df_tmp.iloc[1]
    col4.append(df_tmp.iloc[0])

col4.append(sum(col4))

df_fin['PatientTestedCountChange'] = col4


# Column 5: ConfirmedPositiveCountChange
col5 = []

for pt in pts:
    df_tmp = df.sort_values(['Jurisdiction', 'Confirmed Positive'], ascending=[True, False])
    df_tmp.set_index('Jurisdiction', inplace=True)
    df_tmp = df_tmp.loc[[pt], ['Confirmed Positive']]
    df_tmp = df_tmp.iloc[0] - df_tmp.iloc[1]
    col5.append(df_tmp.iloc[0])

col5.append(sum(col5))

df_fin['ConfirmedPositiveCountChange'] = col5


# Column 6: ConfirmedNegativeCountChange
col6 = []

for pt in pts:
    df_tmp = df.sort_values(['Jurisdiction', 'Confirmed Negative'], ascending=[True, False])
    df_tmp.set_index('Jurisdiction', inplace=True)
    df_tmp = df_tmp.loc[[pt], ['Confirmed Negative']]
    df_tmp = df_tmp.iloc[0] - df_tmp.iloc[1]
    col6.append(df_tmp.iloc[0])

col6.append(sum(col6))

df_fin['ConfirmedNegativeCountChange'] = col6


# Column 7: PTAndCanadianPositivityRatePrct
col7 = []
n = 0

while n < 14:
    col7.append(round(100*(df_fin.iloc[n, 2] / df_fin.iloc[n, 1]), 2))
    n += 1

df_fin['PTAndCanadianPositivityRatePrct'] = col7


# Column 8: CanadianPatientsTestedPerMil
col8 = []
n = 0
natpop = 37589262

while n < 14:
    col8.append(round((df_fin.iloc[n, 1]/natpop)*1000000, 2))
    n += 1

df_fin['CanadianPatientsTestedPerMil'] = col8


# Column 9: PTPatientsTestedPerMil
col9 = []
n = 0
ptpops = [4371316, 5071336, 1369465, 776827, 521542, 971395, 44826, 38780, 14566547, 156947, 8484965, 1174462, 40854]
# PTPops sorted by full PT name (ie. Northwest Territories before Nova Scotia)

while n < 13:
    col9.append(round((df_fin.iloc[n, 1]/ptpops[n])*1000000, 2))
    n += 1

col9.append('N/A')

df_fin['PTPatientsTestedPerMil'] = col9


# Column 10: DateUpdated
col10 = []

for pt in pts:
    df_tmp = df.sort_values(['Jurisdiction', 'Report Date'], ascending=[True, False])
    df_tmp.set_index('Jurisdiction', inplace=True)
    df_tmp = df_tmp.loc[[pt], ['Report Date']]
    col10.append(df_tmp.iloc[0, 0])

col10.append(max(col10))

df_fin['DateUpdated'] = col10


# Column 11: DateLoaded
pts = df_fin['PT'].tolist()
col11 = []
for pt in pts:
    col11.append(now.strftime("%Y-%m-%d (%H:%M:%S)"))

df_fin['DateLoaded'] = col11


# Export
df_fin.to_csv(now.strftime("%Y-%m-%d_%H.%M.%S") + '_transformed.csv', index = False)
