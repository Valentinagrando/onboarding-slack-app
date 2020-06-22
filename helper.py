import subprocess
import json
from simple_salesforce import Salesforce

print("Fetching credentials...")
condaCmdResult = subprocess.run(
    ["conda", "activate", "./env"],
    capture_output=True)
loginCmdResult = subprocess.run(
    ["sfdx", "force:auth:web:login", "-a", "gus", "-r", "https://gus.my.salesforce.com/"],
    capture_output=True)
cmdResult = subprocess.run(
    ["sfdx", "force:org:display", "-u", "gus", "--json"],
    capture_output=True)

payload = json.loads(cmdResult.stdout)
creds = payload["result"]

sf = Salesforce(
    instance_url=creds["instanceUrl"],
    session_id=creds["accessToken"])

aProblemNew =  sf.query("select Initial_Incident__c from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'New'")
aProblemUI =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Under Investigation'")
aProblemAC =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Analysis Complete'")
aProblem3P =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Waiting 3rd Party'")

# test=sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' Initial_Incident__c= limit 1")

print("-------------These are PRBs marked as 'New'")
for problem in aProblemNew['records']:
    incidentNumber = problem['Initial_Incident__c']
    if incidentNumber == None:
        continue
    case = sf.query(f"select CaseNumber, Subject from Case where Id = '{incidentNumber}'")
    for record in case['records']:
        print(record["Subject"])


print("-------------These are PRBs marked as 'Under Investigation'")
for problem in aProblemUI['records']:
    print(problem['Name'])

print("-------------These are PRBs marked as 'Analysis Complete'")
for problem in aProblemAC['records']:
    print(problem['Name'])

print("-------------These are PRBs marked as 'Waiting 3rd Party'")
for problem in aProblem3P['records']:
    print(problem['Name'])


# print(test)
# print("""
# The salesforce client is available as `sf`. IT is authenticated and ready for use.
# The client documentation is available at https://pypi.org/project/simple-salesforce/

# To start exploring try running one of these:
# > dir(sf)
# > sf.ADM_Work__c.describe()
# > sf.query("select Id from ADM_Work__c limit 1")
# """)
