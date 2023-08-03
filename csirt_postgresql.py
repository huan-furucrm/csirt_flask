import psycopg2
from csirt_config_info import get_value_from_config
import json
import numpy as np
def create_conn(database, user, password, host, port):
    conn = None
    try:
        conn = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        print("Connection successful")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn
def close_conn(conn):
    if conn is not None:
        conn.close()
        print("Database connection closed.")

def get_postgresql_table_name():
    return 'salesforce_data_index'

def get_postgresql_fields():
    return ['embedding',]

def get_postgresql_condition():
    return ''

def get_postgresql_query_data(conn, query):
    result = []
    try:
        cur = conn.cursor()
        cur.execute(query)

        result = cur.fetchall()  # fetch all rows
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    return result

def build_postgresql_query_string(table_name, fields, condition):
    field_string = ", ".join(fields)
    if is_empty_string(condition):
        query = f"SELECT {field_string} FROM {table_name};"
    else:
        query = f"SELECT {field_string} FROM {table_name} WHERE {condition};"
    return query

def is_empty_string(input_string):
    return len(input_string) == 0

def convert_data_to_nparray(data):
    list_data = []
    for data_item in data:
        vector_str = json.loads(data_item[0])
        np_array = np.array(vector_str)
        list_data.append(np_array)
    return np.array(list_data)
def get_data_from_postgresql(sql_query):
    postgre_host = get_value_from_config('config\config.ini', 'POSTGRE', 'POSTGRE_HOST')
    postgre_user = get_value_from_config('config\config.ini', 'POSTGRE', 'POSTGRE_USER')
    postgre_passwd = get_value_from_config('config\config.ini', 'POSTGRE', 'POSTGRE_PASSWD')
    postgre_port = get_value_from_config('config\config.ini', 'POSTGRE', 'POSTGRE_PORT')
    postgre_database = get_value_from_config('config\config.ini', 'POSTGRE', 'POSTGRE_DATABASE')
    connection = psycopg2.connect(host=postgre_host, database=postgre_database, user=postgre_user, password=postgre_passwd, port=postgre_port)
    cursor = connection.cursor()
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()

    return data

def add_labels_to_documents(documents):
    labeled_documents = []
    # for document in documents:
    #     for record in document.text["records"]
    #     metadata = {}
    #     metadata["Type"] = get_json_value(document.text["records"])
    #     metadata["Severity"] = data["mssmt__severity__c"]
    #     document.metadata = metadata
    #     labeled_documents.append(document)
    return labeled_documents