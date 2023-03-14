from django.shortcuts import render, HttpResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json



# Create your views here.

def send_email(request):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    #read credentials from file
    with open('credentials.json', 'r') as f:
        data_= json.load(f)
        print("cred_data", type(data_))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(data_, scope)
        # authenticate using the credentials
        client = gspread.authorize(creds)
        open the Google Sheet by its ID
        sheet_id = 'your_sheet_id_here'
        sheet = client.open_by_key(sheet_id).sheet1
        # get all the data from the sheet
        data = sheet.get_all_records()
        print(creds)

    return HttpResponse("ok")
