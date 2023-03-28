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



@api_view(['GET'])
def validate_user_authorities(request):
    response, data = {}, {}
    email = request.GET.get('email',None)
    location = request.GET.get('location', None)
    if not email:                                                             
        response['status_code'], response['message'] = 400, 'email is required'
        return JsonResponse(response)
    sheet = get_client()
    if not sheet:
        response['status_code'], response['message'] = 500, 'Internal error'
        return JsonResponse(response)
    
    all_values = sheet.get_all_records()
    full_row = check_value_exists('Email', email, all_values)
    if full_row:
        if full_row['is_whitelisted'] == 'TRUE':
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            email_cell_row = get_index('Email', email, all_values)
            if email_cell_row != None:
                email_cell_row += 2
            sheet.update_cell(email_cell_row, 9, utc_now.strftime('%Y-%m-%d %H:%M:%S'))
            if location:
                sheet.update_cell(email_cell_row, 8, location)
            data['is_whitelisted'] = True
        else:
            data['is_whitelisted'] = False
        response['data'],response['status_code']=data, 200
        response['message'] = 'User is whitelisted'
        return JsonResponse(response)
    else:
        data['is_whitelisted'] = False
        response['data'],response['status_code'], response['message']=data, 404, 'User does not exist'
        return JsonResponse(response)
