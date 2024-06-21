# You can use this code locally to run one-off jobs.

import requests

token = "your-private-app-key-here"

users = ["john.doe@example.com", "jane.doe@example.com"]

for user in users:

  user_email_address = user
  
  emails_to_update = []

  def checkEmailSentByUser(url,querystring,headers):
    try:
      response = requests.request("GET", url, headers=headers, params=querystring)
      response_json = response.json()

      if 'paging' in response_json:
        after = response_json['paging']['next']['after']
      else:
        after = False
      emails = response_json['results']

      for email in emails:
        email_id = email['id']
        sender_email_address = email['from']['replyTo']
        email_type = email['type']
        excluded_types = ["BATCH_EMAIL", "AB_EMAIL", "LOCALTIME_EMAIL"]
        automated_email_types = ["AUTOMATED_EMAIL", "AUTOMATED_AB_EMAIL"]
        email_is_published = email['isPublished']
        email_workflows = email['workflowNames']
        active_workflows_using_this_email = []
        if len(email_workflows) > 0:
          for workflow in email_workflows:
            if not ("❌" in workflow or "🔴" in workflow or "🚧" in workflow or "📥" in workflow):
              active_workflows_using_this_email.append(workflow)
        if (len(active_workflows_using_this_email) > 0 and email_type == "AUTOMATED_EMAIL") or (len(active_workflows_using_this_email) > 0 and email_type == "AUTOMATED_AB_EMAIL") or (len(email_workflows) == 0 and email_type not in automated_email_types):
          if email_type not in excluded_types:
            if email_is_published:
              if sender_email_address == user_email_address:
                print(f"email {email_id} is an active {email_type} sent by {user_email_address} and included in these active workflows {active_workflows_using_this_email}")
                email_url = f"https://app.hubspot.com/email/2694792/details/{email_id}/performance"
                emails_to_update.append(email_url)
    
    except requests.exceptions.RequestException as e:
      print(f"A Requests error occurred: {e}")
      return {"after": False}
    except Exception as e:
      print(f"An error occurred: {e}")
      return {"after": False}
    return {"after": after}
    

  url = "https://api.hubapi.com/marketing/v3/emails/"
  querystring = {"limit":"300","workflowNames":"true"}
  headers = {
    'accept': "application/json",
    'authorization': f"Bearer {token}"
  }
  after = True
  while after:
    result = checkEmailSentByUser(url,querystring,headers)
    after = result.get('after', False)
    querystring = {"limit":"300","workflowNames":"true","after":f"{after}"}
  if len(emails_to_update) > 0:
    emails_to_update_str = "\n".join(emails_to_update)
    print(emails_to_update_str)

  else:
    print("This deactivated user isn't sending emails")
