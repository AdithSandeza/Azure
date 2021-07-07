import subprocess
import json
import os 
from dotenv import load_dotenv,find_dotenv
import csv
from datetime import datetime
from pytz import timezone
import pytz



date = datetime.now(tz=pytz.utc)
date = date.astimezone(timezone('US/Pacific'))


dotenvPath = load_dotenv(find_dotenv())
userName = os.getenv('AZURE_CLIENT_ID')
password = os.getenv('AZURE_CLIENT_SECRET')
tenant = os.getenv('TENANT')
# tenant = os.environ('AZURE_TENANT_ID')

startDate = datetime.today().replace(day=1).strftime('%Y-%m-%d')
endDate = datetime.today().strftime('%Y-%m-%d')
month = datetime.today().month
startYear = datetime.today().replace(month=1,day=1).strftime('%Y-%m-%d')
firstMonthStartDay = datetime.today().replace(month = month-2,day =1).strftime('%Y-%m-%d')
# print(startYear)

def azureAccounts():
    ## Login with username and password
    login = json.loads(subprocess.check_output(('az login --service-principal -u {} -p {} --tenant {}').format(userName,password,tenant),shell=True))
    ## list all accounts
    subscriptions = json.loads(subprocess.check_output('az account list --all', shell=True))
    
    accounts = []
    for i in subscriptions:
      
        if(i["state"] == "Enabled"):
            accountName = i['name']
            subscriptionId = i['id']

            ## GET ROLES, turn argument to false to ignore classic admin
            monthToDate =  json.loads(subprocess.check_output(('az consumption usage list --subscription {} --start-date {} --end-date {} -m --query "[].pretaxCost.to_number(@)|sum([])"  ').format(subscriptionId,startDate,endDate), shell=True).decode('utf-8'))

            yearToDate =  json.loads(subprocess.check_output(('az consumption usage list --subscription {} --start-date {} --end-date {} -m --query "[].pretaxCost.to_number(@)|sum([])"  ').format(subscriptionId,startYear,endDate), shell=True).decode('utf-8'))
  
            lastThreeMonths =  json.loads(subprocess.check_output(('az consumption usage list --subscription {} --start-date {} --end-date {} -m --query "[].pretaxCost.to_number(@)|sum([])"  ').format(subscriptionId,firstMonthStartDay,endDate), shell=True).decode('utf-8'))
         
            accountDetails = {"AccountName":accountName,"SubscriptionId":subscriptionId,"LastThreeMonths":lastThreeMonths,"MonthToDate":monthToDate,"YearToDate":yearToDate}
            accounts.append(accountDetails)
    return accounts;
            


        
try:
    getUsers = azureAccounts()    
   
   
    fields = ["AccountName","SubscriptionId","Last-3-Months","Month-to-Date","Year-to-Date"]
    rows = []
    for i in getUsers:
        row = []
        row.extend((i['AccountName'],i['SubscriptionId'],i['LastThreeMonths'],i['MonthToDate'],i['YearToDate']))
        rows.append(row)

   
   
    filename = "azure_Billing_"+ str(datetime.now()).replace(':','_')+ ".csv"

# writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)

        # writing the fields
        csvwriter.writerow(fields)

        # writing the data rows
        csvwriter.writerows(rows)
except Exception as e :
    print("Exception:",e)


