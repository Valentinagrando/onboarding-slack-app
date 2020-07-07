import subprocess
import json
from datetime import datetime, timedelta, date
import pandas as pd
from simple_salesforce import Salesforce

print("Fetching credentials...")
# condaCmdResult = subprocess.run(
#     ["conda", "activate", "./env"],
#     capture_output=True)
# loginCmdResult = subprocess.run(
#     ["sfdx", "force:auth:web:login", "-a", "gus", "-r", "https://gus.my.salesforce.com/"],
#     capture_output=True)
cmdResult = subprocess.run(
    ["sfdx", "force:org:display", "-u", "gus", "--json"],
    capture_output=True)

payload = json.loads(cmdResult.stdout)
creds = payload["result"]

sf = Salesforce(
    instance_url=creds["instanceUrl"],
    session_id=creds["accessToken"])

today = date.today()
def workdays(d, end, excluded=(6, 7)):
    days = []
    since = 0
    if d > end.date() and d != end.date():
        while d > end.date():
            if end.date().isoweekday() not in excluded:
                since -= 1
            end += timedelta(days=1)
        return since
    while d < end.date():
        if d.isoweekday() not in excluded:
            days.append(d)
        d += timedelta(days=1)
    
    if len(days) == 1 and days[0] == datetime.strptime(str(d), "%Y-%m-%d"):
        return 0
    return len(days)

def needsRetro():
    today = date.today()
    retroReinterate=[]
    retrosList = sf.query("select CreatedDate, Initial_Incident__c, Name, Id, Problem_Priority__c from SM_Problem__c where Cloud__c = 'Heroku' AND (Problem_State__c = 'New' OR Problem_State__c = 'Under Investigation')")
    for retro in retrosList['records']:
        
        incidentNumber = retro['Initial_Incident__c']
        if incidentNumber == None:
            case = sf.query(f"select CaseNumber, Subject, Initial_Incident__c, Cloud__c from Case where SM_Problem__c = '{retro['Id']}'")
            if case['totalSize'] == 0:
                 continue
        else:
            case = sf.query(f"select CaseNumber, Subject, SM_Problem__c from Case where Id = '{incidentNumber}'")
        
        caseName = case['records'][0]['Subject']
        dateCreated = datetime.strptime(retro['CreatedDate'][0:10], "%Y-%m-%d")

        if retro['Problem_Priority__c'] == 'Sev0' or retro['Problem_Priority__c'] == 'Sev1':
            retroDue =  dateCreated + timedelta(days = 3)
            weekend = 0
            if retroDue.isoweekday() == 6:
                weekend = 1
            elif retroDue.isoweekday() == 7:
                weekend = 2
            while retroDue.isoweekday() == 6 or retroDue.isoweekday() == 7:
                retroDue = retroDue + timedelta(days = 1)
            if weekend != 0:
                weekend-=1
            retroDue+=timedelta(days = weekend)
            workdaysUntil = workdays(today, retroDue)
            if  abs(workdaysUntil) >= 196:
                continue
            if workdaysUntil > 3 or workdaysUntil < 0:
                retroReinterate.append((caseName, retro['Problem_Priority__c'], workdaysUntil,retroDue.date()))
            else:
                retroReinterate.append((caseName, retro['Problem_Priority__c'], workdaysUntil,retroDue.date()))


        elif retro['Problem_Priority__c'] == 'Sev2' or retro['Problem_Priority__c'] == 'Sev3' or retro['Problem_Priority__c'] == 'Sev4':
            retroDue =  dateCreated + timedelta(days = 5)
            weekend = 0
            if retroDue.isoweekday() == 6:
                    weekend = 1
            elif retroDue.isoweekday() == 7:
                weekend = 2
            while retroDue.isoweekday() == 6 or retroDue.isoweekday() == 7:
                retroDue = retroDue + timedelta(days = 1)
            if weekend != 0:
                weekend-=1
            workdaysUntil = workdays(today, retroDue)
            retroDue+=timedelta(days = weekend)
            if  abs(workdaysUntil) >= 196:
                continue
            if workdaysUntil > 5 or workdaysUntil < 0:
                retroReinterate.append((caseName, retro['Problem_Priority__c'], workdaysUntil,retroDue.date()))
            else:
                retroReinterate.append((caseName, retro['Problem_Priority__c'], workdaysUntil, retroDue.date()))
    print("Returning Retro function")
    return retroReinterate


def needsAAR():
    AARinterate = []
    AARList = sf.query("select CreatedDate, Initial_Incident__c, Name, Id, Problem_Priority__c, AARReviewDate__c from SM_Problem__c where Cloud__c = 'Heroku'")
    for aar in AARList['records']:
        incidentNumber = aar['Initial_Incident__c']
        if incidentNumber == None:
            case = sf.query(f"select CaseNumber, Subject, Initial_Incident__c, Cloud__c from Case where SM_Problem__c = '{aar['Id']}'")
            if case['totalSize'] == 0:
                 continue
            
        else:
            case = sf.query(f"select CaseNumber, Subject, SM_Problem__c from Case where Id = '{incidentNumber}'")

        if aar['AARReviewDate__c'] == None:
            # print("Analysing AAR")
            caseName = case['records'][0]['Subject']
            dateCreated = datetime.strptime(aar['CreatedDate'][0:10], "%Y-%m-%d")

            if aar['Problem_Priority__c'] == 'Sev0' or aar['Problem_Priority__c'] == 'Sev1':
                aarDue =  dateCreated + timedelta(days = 1)
                if abs(workdays(today,aarDue)) >= 196:
                    continue
                weekend = 0
                if aarDue.isoweekday() == 6:
                    weekend = 1
                elif aarDue.isoweekday() == 7:
                    weekend = 2
                while aarDue.isoweekday() == 6 or aarDue.isoweekday() == 7:
                    aarDue = aarDue + timedelta(days = 1)
                if weekend != 0:
                    weekend-=1
                aarDue+=timedelta(days = weekend)
                workdaysUntil = workdays(today, aarDue)
                if  abs(workdaysUntil) >= 196:
                    continue
                if workdaysUntil > 1 or workdaysUntil < 0:
                    AARinterate.append((caseName, aar['Problem_Priority__c'], workdaysUntil,aarDue.date()))
                else:
                    AARinterate.append((caseName, aar['Problem_Priority__c'], workdaysUntil,aarDue.date()))


            elif aar['Problem_Priority__c'] == 'Sev2' or aar['Problem_Priority__c'] == 'Sev3' or aar['Problem_Priority__c'] == 'Sev4':
                aarDue =  dateCreated + timedelta(days = 2)
                if abs(workdays(today,aarDue)) >= 196:
                    continue
                weekend = 0
                if aarDue.isoweekday() == 6:
                        weekend = 1
                elif aarDue.isoweekday() == 7:
                    weekend = 2
                while aarDue.isoweekday() == 6 or aarDue.isoweekday() == 7:
                    aarDue = aarDue + timedelta(days = 1)
                if weekend != 0:
                    weekend-=1
                aarDue+=timedelta(days = weekend)
                workdaysUntil = workdays(today, aarDue)
                if  abs(workdaysUntil) >= 196:
                    continue
                if workdaysUntil > 2 or workdaysUntil < 0:
                    AARinterate.append((caseName, aar['Problem_Priority__c'], workdaysUntil,aarDue.date()))
                else:
                    AARinterate.append((caseName, aar['Problem_Priority__c'], workdaysUntil,aarDue.date()))
            print("Finished analyzing")
        else:
            continue
    print("Returning AAR function")
    return AARinterate