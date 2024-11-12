from __future__ import print_function

import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
import asyncio

async def google_function(script_id, function, *parameters):
    SCOPES = ['https://www.googleapis.com/auth/script.projects', 	'https://www.googleapis.com/auth/script.external_request', 	'https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/calendar']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('script', 'v1', credentials=creds)
    if parameters != None:
        ls = []
        for x in parameters:
            ls.append(x)
    # Create an execution request object.
        request = {
            "function": function,
            "parameters": ls,
            "devMode": "true"}
    else:
        request = {
            "function": function,
            "devMode": "true"}

    try:
        # Make the API request.
        response = service.scripts().run(scriptId=script_id,
                                         body=request).execute()
        if 'error' in response:
            # The API executed, but the script returned an error.
            # Extract the first (and only) set of error details. The values of
            # this object are the script's 'errorMessage' and 'errorType', and
            # a list of stack trace elements.
            error = response['error']['details'][0]
            print(f"Script error message: {0}.{format(error['errorMessage'])}")

            if 'scriptStackTraceElements' in error:
                # There may not be a stacktrace if the script didn't start
                # executing.

                print("Script error stacktrace")
                '''
                for trace in error['scriptStackTraceElements']:
                    print(f"\t{0}: {1}."
                          f"{format(trace['function'], trace['lineNumber'])}")
                '''
                return "nill"
        else:
            # The structure of the result depends upon what the Apps Script
            # function returns. Here, the function returns an Apps Script
            # Object with String keys and values, and so the result is
            # treated as a Python dictionary (folder_set).
            result = response['response'].get('result', {})
            return result
    except HttpError as error:
        # The API encountered a problem before the script started executing.
        print(f"An error occurred: {error}")
        print(error.content)

async def import_form(script_id):
    a =  await google_function(script_id, "settings_form_python")
    return(a)

if __name__ == "__main__":
    pass