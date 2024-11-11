from flask import Blueprint, jsonify, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.db_operations import get_credentials_by_superid

appfolders = Blueprint('appfolders', __name__)


@appfolders.route('/delete_folder/<folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    super_id = request.args.get('super_id')  # Get super_id from query parameters
    credentials = get_credentials_by_superid(super_id)
    if not credentials:
        return jsonify({'status': False, 'message': 'Invalid super_id or no credentials found'}), 400

    service = build('drive', 'v3', credentials=credentials)

    try:
        # Call the Drive API to delete the folder
        service.files().delete(fileId=folder_id).execute()
        return jsonify({'status': True, 'message': 'Folder deleted successfully.'}), 200

    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@appfolders.route('/create_folder', methods=['POST'])
def create_folder():
    super_id = request.json.get('super_id')  # Get super_id from request body
    credentials = get_credentials_by_superid(super_id)
    if not credentials:
        return jsonify({'status': False, 'message': 'Invalid super_id or no credentials found'}), 400

    service = build('drive', 'v3', credentials=credentials)

    folder_name = request.json.get('folder_name')
    permissions = request.json.get('permissions', [])

    if not folder_name:
        return jsonify({'status': False, 'message': 'Folder name is required.'}), 400

    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    try:
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')

        for perm in permissions:
            permission_body = {
                'role': perm.get('role', 'reader'),
                'type': perm.get('type', 'user'),
                'emailAddress': perm.get('emailAddress')
            }
            service.permissions().create(
                fileId=folder_id,
                body=permission_body,
                sendNotificationEmail=False
            ).execute()
        return jsonify({'status': True, 'folder_id': folder_id, 'message': 'Folder created successfully.'}), 201

    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

@appfolders.route('/get_folders_list', methods=['GET'])
def get_folders_list():
    super_id = request.args.get('super_id')  # Get super_id from query parameters
    credentials = get_credentials_by_superid(super_id)
    if not credentials:
        return jsonify({'status': False, 'message': 'Invalid super_id or no credentials found'}), 400

    service = build('drive', 'v3', credentials=credentials)

    query = "mimeType='application/vnd.google-apps.folder'"

    try:
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, owners, permissions)",
            pageSize=1000
        ).execute()

        items = results.get('files', [])
        if not items:
            return jsonify({'status': True, 'data': [], 'message': 'No folders found.'}), 404
        else:
            return jsonify({'status': True, 'data': items, 'message': None}), 200

    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
















# SERVICE_ACCOUNT_FILE = r'C:\pavan\PAVAN\google_APIS\Google_apis_test\config.json'
#
# @appfolders.route('/delete_folder/<folder_id>', methods=['DELETE'])
# def delete_folder(folder_id):
#     # Authenticate and create the Google Drive API client
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=['https://www.googleapis.com/auth/drive']
#     )
#
#     service = build('drive', 'v3', credentials=credentials)
#
#     try:
#         # Call the Drive API to delete the folder
#         service.files().delete(fileId=folder_id).execute()
#         return jsonify({'status': True, 'message': 'Folder deleted successfully.'}), 200
#
#     except Exception as e:
#         return jsonify({'status': False, 'message': str(e)}), 500
#
#
# @appfolders.route('/create_folder', methods=['POST'])
# def create_folder():
#     # Authenticate and create the Google Drive API client
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=['https://www.googleapis.com/auth/drive']
#     )
#
#     service = build('drive', 'v3', credentials=credentials)
#
#     # Get folder name and permissions from request
#     folder_name = request.json.get('folder_name')
#     permissions = request.json.get('permissions', [])
#
#     if not folder_name:
#         return jsonify({'status': False, 'message': 'Folder name is required.'}), 400
#
#     # Create the folder
#     folder_metadata = {
#         'name': folder_name,
#         'mimeType': 'application/vnd.google-apps.folder'
#     }
#
#     try:
#         # Create the folder
#         folder = service.files().create(body=folder_metadata, fields='id').execute()
#         folder_id = folder.get('id')
#
#         # Set permissions for the folder
#         for perm in permissions:
#             permission_body = {
#                 'role': perm.get('role', 'reader'),  # Default role is 'reader'
#                 'type': perm.get('type', 'user'),    # Default type is 'user'
#                 'emailAddress': perm.get('emailAddress')  # Email address must be provided for 'user' type
#             }
#
#             # Create the permission
#             service.permissions().create(
#                 fileId=folder_id,
#                 body=permission_body,
#                 sendNotificationEmail=False  # Set to True to send notifications
#             ).execute()
#         return jsonify({'status': True, 'folder_id': folder_id, 'message': 'Folder created successfully.'}), 201
#
#     except Exception as e:
#         return jsonify({'status': False, 'message': str(e)}), 500
#
#
# @appfolders.route('/get_folders_list', methods=['GET'])
# def get_folders_list():
#     # Authenticate and create the Google Drive API client
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE,
#         scopes=['https://www.googleapis.com/auth/drive.readonly']
#     )
#
#     service = build('drive', 'v3', credentials=credentials)
#
#     # Define the query to find all folders
#     query = "mimeType='application/vnd.google-apps.folder'"
#
#     try:
#         # Make the API call to list folders
#         results = service.files().list(
#             q=query,
#             fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, owners, permissions)",
#             pageSize=1000  # Adjust this number if needed
#         ).execute()
#
#         items = results.get('files', [])
#         if not items:
#             return jsonify({'status': True, 'data': [], 'message': 'No folders found.'}), 404
#         else:
#             return jsonify({'status': True, 'data': items, 'message': None}), 200
#
#     except Exception as e:
#         return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
