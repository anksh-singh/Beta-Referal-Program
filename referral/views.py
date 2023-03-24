from django.shortcuts import render, HttpResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json
from django.http import JsonResponse
from rest_framework.decorators import api_view
# from .helper_function import generate_referral_code, valid_json
from decouple import config
import datetime

# Create your views here.


def get_row_number(key, value, list_of_dicts):
    for i, dictionary in enumerate(list_of_dicts):
        if key in dictionary and dictionary[key] == value:
            return i
    return None

def get_client():
    scope = [config('GOOGLE_SHEET_SCOPE')]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config('SHEET_ID')).sheet1
        return sheet
    except Exception as e:
        print("error while fetching sheet data",e)
        return False


def send_email(request):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    #read credentials from file
    with open('credentials.json', 'r') as f:
        data_= json.load(f)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(data_, scope)
        # authenticate using the credentials
        client = gspread.authorize(creds)
        # open the Google Sheet by its ID
        sheet_id = 'your_sheet_id_here'
        sheet = client.open_by_key(sheet_id).sheet1
        # get all the data from the sheet
        data = sheet.get_all_records()
        

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
    full_row = fetch_row_value_exist('Email', email, all_values)
    if full_row:
        if full_row['is_whitelisted'] == 'TRUE':
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            email_cell_row = get_row_number('Email', email, all_values)
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


@api_view(['GET'])
def user_landing_page(request):
    response, data = {}, {}
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    email, wallet_address = body_data.get('email',None), body_data.get('wallet_address', None)
    if not email or not wallet_address:
        response['status_code'], response['message'] = 400, 'email and wallet address both are required fields'
        return JsonResponse(response)

    sheet = get_client()
    if not sheet:
        response['status_code'], response['message'] = 500, 'Internal error'
        return JsonResponse(response)

    all_values = sheet.get_all_records()
    full_row = fetch_row_value_exist('Email', email, all_values)

    if full_row:
        if full_row['is_whitelisted'] == "TRUE":
            email_cell_row = get_row_number('Email', email, all_values)
            if email_cell_row != None:
                email_cell_row += 2
            if full_row['Referred by'] is not None and not full_row['Wallet Address']:
                referred_by_row = fetch_row_value_exist('Email', full_row['Referred by'], all_values)
                if referred_by_row:
                    referred_by_user_points = referred_by_row['Points']
                    if referred_by_user_points in [None, '']:
                        referred_by_user_points = 0
                    referred_by_row_index = get_row_number('Email', referred_by_row['Email'], all_values)
                    referred_by_row_index += 2
                    sheet.update_cell(referred_by_row_index, 6, int(referred_by_user_points)+1)
                    referred_by_successful_referral = referred_by_row['Successful Referrals']
                    if referred_by_successful_referral in [None, '']:
                        referred_by_successful_referral = 0
                    sheet.update_cell(referred_by_row_index, 10, int(referred_by_successful_referral)+1)
                
            sheet.update_cell(email_cell_row, 3, wallet_address)
            user_referral_code = full_row['Referral Code']
            if not full_row['Referral Code']:
                while True:
                    unique_referral_code = generate_referral_code()
                    if not fetch_row_value_exist('Referral Code', unique_referral_code, all_values):
                        sheet.update_cell(email_cell_row, 4, unique_referral_code)
                        break
                user_referral_code = unique_referral_code
            referral_count = get_count_of_rows('Referred by', email, all_values)
            data['number_of_referrals'] = referral_count
            data['successful_referrals_count'] = full_row['Successful Referrals']
            if user_referral_code:
                unique_referral_code = f"https://www.frontier.xyz/bundle-dapp?ref={user_referral_code}"
            else:
                unique_referral_code = ""

            data['email'], data['wallet_address'] = email, wallet_address
            data['referral_url'], data['points']  = unique_referral_code, full_row['Points']
            response['data'] = data
            response['status_code'], response['message'] = 200, 'wallet connected successfully'
        else:
            data['is_whitelisted'] = False
            response['data'] = data
            response['status_code'], response['message']  = 403, 'User is not whitelisted'
    else:
        response['status_code'], response['message'] = 404, 'User does not exist'

    return JsonResponse(response)



def fetch_row_value_exist(key, value, list_of_dicts):
    for d in list_of_dicts:
        if key in d and d[key] == value:
            return d
    return False

