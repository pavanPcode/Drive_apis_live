from flask import Blueprint, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from services.db_operations import save_file_data,get_credentials_by_superid
import os
from googleapiclient.http import MediaFileUpload
import tempfile
import requests
import string
import random

appdrive = Blueprint('appdrive', __name__)

#SERVICE_ACCOUNT_FILE = r'C:\pavan\PAVAN\google_APIS\Google_apis_test\config.json'

def generate_short_code(length=8):
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choice(characters) for _ in range(length))
        # if not URL.query.filter_by(short_url=short_url).first():
        #     return short_url
        return short_url


@appdrive.route('/upload_image/<folder_id>', methods=['POST'])
def upload_image(folder_id):
    super_id = request.form.get('super_id')
    description = request.form.get('description')

    # Check if the required fields are provided
    if not super_id:
        return jsonify({'status': False, 'message': 'No super_id provided'}), 400
    if 'file' not in request.files:
        return jsonify({'status': False, 'message': 'No file provided'}), 400

    # Authenticate and create the Google Drive API client
    credentials = get_credentials_by_superid(super_id)
    if not credentials:
        return jsonify({'status': False, 'message': 'No credentials found'}), 400

    service = build('drive', 'v3', credentials=credentials)

    # Get the uploaded file from the request
    file = request.files['file']

    # Save the uploaded file to a temporary location
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            file.save(temp_file_path)

        # Define metadata for the file
        file_metadata = {
            'name': file.filename,
            'parents': [folder_id]
        }

        # Upload the file
        media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        # Set the file permissions to make it public
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=uploaded_file.get('id'),
            body=permission
        ).execute()

        # Construct a public URL for the uploaded file
        #file_url = f"https://lh3.googleusercontent.com/d/{uploaded_file.get('id')}=w1000?authuser=0"
        file_url = f"https://drive.google.com/thumbnail?id={uploaded_file.get('id')}&sz=s4000"
        tiny_url = generate_short_code()

        # Save file info to the database
        db_response = save_file_data(uploaded_file.get('id'), uploaded_file.get('name'), file_url, tiny_url, super_id,
                                     description)

        return jsonify({
            'status': db_response['status'],
            'message': db_response['message'],
            'data': {
                'file_id': uploaded_file.get('id'),
                'file_name': uploaded_file.get('name'),
                'file_url': file_url,
                'tiny_url': f'https://googledriveapis.azurewebsites.net/{tiny_url}'
            }
        }), 200 if db_response['status'] else 500

    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

    finally:
        # Ensure the temporary file is deleted
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except PermissionError:
                pass


# @appdrive.route('/upload_image/<folder_id>', methods=['POST'])
# def upload_image(folder_id):
#     # Authenticate and create the Google Drive API client
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=['https://www.googleapis.com/auth/drive']
#     )
#     service = build('drive', 'v3', credentials=credentials)
#
#     super_id = request.form['super_id']
#     # Get the uploaded file from the request
#     file = request.files.get('file')
#     if file is None:
#         return jsonify({'status': False, 'message': 'No file provided'}), 400
#     if super_id is None:
#         return jsonify({'status': False, 'message': 'No super_id provided'}), 400
#
#     # Save the uploaded file to a temporary location
#     temp_file_path = None
#     try:
#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             temp_file_path = temp_file.name
#             file.save(temp_file_path)
#
#         # Define metadata for the file
#         file_metadata = {
#             'name': file.filename,
#             'parents': [folder_id]
#         }
#
#         # Upload the file
#         media = MediaFileUpload(temp_file_path, mimetype=file.content_type)
#         uploaded_file = service.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields='id, name'
#         ).execute()
#
#         # Set the file permissions to make it public
#         permission = {
#             'type': 'anyone',
#             'role': 'reader'
#         }
#         service.permissions().create(
#             fileId=uploaded_file.get('id'),
#             body=permission
#         ).execute()
#
#         # Construct a public URL for the uploaded file
#         #file_url = f"https://drive.google.com/uc?id={uploaded_file.get('id')}"
#         file_url = f"https://lh3.googleusercontent.com/d/{uploaded_file.get('id')}=w1000?authuser=0"
#         tiny_url = generate_short_code()
#         # Save file info to the database
#         db_response = save_file_data(uploaded_file.get('id'), uploaded_file.get('name') , file_url, tiny_url,super_id)
#
#         return jsonify({
#             'status': db_response['status'],
#             'message': db_response['message'],
#             'data': {
#                 'file_id': uploaded_file.get('id'),
#                 'file_name': uploaded_file.get('name'),
#                 'file_url': file_url,  # Include the public URL
#                 'tiny_url':f'http://127.0.0.1:5000/{tiny_url}'
#             }
#         }), 200 if db_response['status'] else 500
#
#     except Exception as e:
#         return jsonify({'status': False, 'message': str(e)}), 500
#
#     finally:
#         # Ensure the temporary file is deleted
#         if temp_file_path and os.path.exists(temp_file_path):
#             try:
#                 os.remove(temp_file_path)
#             except PermissionError:
#                 pass  # Skip if file still can't be deleted; it will eventually be removed
#
