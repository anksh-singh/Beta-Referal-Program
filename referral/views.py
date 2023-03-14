from django.shortcuts import render, HttpResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials



# Create your views here.

def send_email(request):
    #fetch all the white listed users
    # set up authentication
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    # open the Google Sheet using sheet ID
    sheet_id = '1G6PzAEXCBIPxNSF12f1pw05IyS4bl90jocX3xpE3Pjc'
    sheet = client.open_by_key(sheet_id).sheet1
    print(sheet)

    # # read the data from the sheet
    # data = sheet.get_all_values()
    # print(data)

    return HttpResponse("ok")
