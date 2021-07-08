## subprocess to execute cli commands 
import subprocess
## json to load json data
import json
## os to get dotenv file location
import os 
## find and load dotenv file 
from dotenv import load_dotenv,find_dotenv
## csv to write data to a csv file 
import csv
## datetime to get date details 
from datetime import datetime
## timzone to get specific timezone 
from pytz import timezone
import pytz
## calender to get date range 
import calendar



date = datetime.now(tz=pytz.utc)
date = date.astimezone(timezone('US/Pacific'))

## load the credentials from .env file (AZURE_CLIENT_ID,AZURE_CLIENT_SECRET,TENANT)
dotenvPath = load_dotenv(find_dotenv())
userName = os.getenv('AZURE_CLIENT_ID')
password = os.getenv('AZURE_CLIENT_SECRET')
tenant = os.getenv('TENANT')

## get first and todays date 
startDate = datetime.today().replace(day=1).strftime('%Y-%m-%d')
endDate = datetime.today().strftime('%Y-%m-%d')

##get current month and year 
month = datetime.today().month
year = datetime.today().year

## get starting date of the year 
startYear = datetime.today().replace(month=1,day=1).strftime('%Y-%m-%d')

## start and end date for the first month 
getFirstMonth_date = datetime(year ,month-2,1)
firstMonthRange = calendar.monthrange(getFirstMonth_date.year, getFirstMonth_date.month)[1]
firstMonthStartDay = datetime(year,month-2,1).strftime('%Y-%m-%d')
firstMonthEndDay = datetime(year,month-2,firstMonthRange).strftime('%Y-%m-%d')

## start and end date for the second month 

getSecondMonth_date = datetime(year ,month-1,1)
secondMonthRange = calendar.monthrange(getSecondMonth_date.year, getSecondMonth_date.month)[1]
secondMonthStartDay = datetime(year,month-1,1).strftime('%Y-%m-%d')
secondMonthEndDay = datetime(year,month-1,secondMonthRange).strftime('%Y-%m-%d')


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
            firstMonth =  json.loads(subprocess.check_output(('az consumption usage list --subscription {} --start-date {} --end-date {} -m --query "[].pretaxCost.to_number(@)|sum([])"  ').format(subscriptionId,firstMonthStartDay,firstMonthEndDay), shell=True).decode('utf-8'))
            secondMonth =  json.loads(subprocess.check_output(('az consumption usage list --subscription {} --start-date {} --end-date {} -m --query "[].pretaxCost.to_number(@)|sum([])"  ').format(subscriptionId,secondMonthStartDay,secondMonthEndDay), shell=True).decode('utf-8'))

            accountDetails = {"AccountName":accountName,"SubscriptionId":subscriptionId,"FirstMonth":firstMonth,"SecondMonth":secondMonth,"ThirdMonth":monthToDate,"MonthToDate":monthToDate,"YearToDate":yearToDate}
            accounts.append(accountDetails)
    return accounts;
            


        
try:
    getUsers = azureAccounts()
    ## get names of the months 
    firstMonthName = datetime.today().replace(month = month-2).strftime('%B')
    secondMonthName = datetime.today().replace(month = month-1).strftime('%B')
    thirdMonthName = datetime.today().strftime('%B')

    ## writing field names for the csv [AccountName,SubscriptionId,firstMonthNamesecondMonthName,thirdMonthName,Month-to-Date,Year-to-Date]
    fields = ["AccountName","SubscriptionId",firstMonthName,secondMonthName,thirdMonthName,"Month-to-Date","Year-to-Date"]    
   

    rows = []
    for i in getUsers:
        row = []
        ## get details for each row 
        row.extend((i['AccountName'],i['SubscriptionId'],i['FirstMonth'],i['SecondMonth'],i['ThirdMonth'],i['MonthToDate'],i['YearToDate']))
        
        ## append all row to rows 
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


