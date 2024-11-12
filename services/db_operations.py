import mysql.connector
from mysql.connector import Error
import configparser
from google.oauth2 import service_account
import json

CONFIG_PATH = 'dbConfig.ini'
dbname = 'db_live'
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
dbinfo = {
            "host": config.get(dbname, "host"),
            "database": config.get(dbname, "database"),
            "user": config.get(dbname, "user"),
            "password": config.get(dbname, "password"),
        }


def get_credentials_by_superid(super_id):
    connection = mysql.connector.connect(**dbinfo)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT service_account_json FROM google_service_accounts WHERE super_id = %s"
    cursor.execute(query, (super_id,))

    result = cursor.fetchone()
    connection.close()

    if result:
        service_account_info = json.loads(result['service_account_json'])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        return credentials
    else:
        print("No credentials found for super_id:", super_id)
        return None


# # Usage example
# super_id = 1
# credentials = get_credentials_by_superid(super_id)
# if credentials:
#     print("Credentials loaded successfully.")


def save_file_data(file_id, file_name, original_url, tiny_url,super_id,description):
    try:
        # Set up your database connection
        connection = mysql.connector.connect(**dbinfo)
        if connection.is_connected():
            cursor = connection.cursor()

            # SQL query to insert data into the table
            sql_query = """
            INSERT INTO drive_uploaded_files (file_id, file_name, original_url, tiny_url,super_id,description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            data_tuple = (file_id, file_name, original_url, tiny_url,super_id,description)

            # Execute the query and commit the transaction
            cursor.execute(sql_query, data_tuple)
            connection.commit()

            return {'status': True, 'message': 'File data saved successfully'}

    except Error as e:
        return {'status': False, 'message': f"Error: {str(e)}"}

    finally:
        # Ensure resources are released
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_original_url(tiny_url):
    try:
        connection = mysql.connector.connect(**dbinfo)
        cursor = connection.cursor(dictionary=True)

        query = "SELECT original_url FROM drive_uploaded_files WHERE tiny_url = %s"
        cursor.execute(query, (tiny_url,))

        result = cursor.fetchone()
        connection.close()
        if result:
            return result['original_url']
        else:
            False

    except Error as e:
        print(e)
        return False