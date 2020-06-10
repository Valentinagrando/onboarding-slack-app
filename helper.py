import subprocess
import json
from simple_salesforce import Salesforce

print("Fetching credentials...")
cmdResult = subprocess.run(
    ["sfdx", "force:org:display", "-u", "gus", "--json"],
    capture_output=True)

payload = json.loads(cmdResult.stdout)
creds = payload["result"]

sf = Salesforce(
    instance_url=creds["instanceUrl"],
    session_id=creds["accessToken"])

aProblemNew =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'New'")
aProblemUI =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Under Investigation'")
aProblemAC =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Analysis Complete'")
aProblem3P =  sf.query("select Name from SM_Problem__c where Cloud__c = 'Heroku' AND Problem_State__c = 'Waiting 3rd Party'")

print("-------------These are PRBs marked as 'New'")
for problem in aProblemNew['records']:
    print(problem['Name'])

print("-------------These are PRBs marked as 'Under Investigation'")
for problem in aProblemUI['records']:
    print(problem['Name'])

print("-------------These are PRBs marked as 'Analysis Complete'")
for problem in aProblemAC['records']:
    print(problem['Name'])

print("-------------These are PRBs marked as 'Waiting 3rd Party'")
for problem in aProblem3P['records']:
    print(problem['Name'])

# print("""
# The salesforce client is available as `sf`. IT is authenticated and ready for use.
# The client documentation is available at https://pypi.org/project/simple-salesforce/

# To start exploring try running one of these:
# > dir(sf)
# > sf.ADM_Work__c.describe()
# > sf.query("select Id from ADM_Work__c limit 1")
# """)
