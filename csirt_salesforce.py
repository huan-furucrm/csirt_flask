from llama_index import Document, download_loader, StorageContext, VectorStoreIndex
from csirt_config_info import get_value_from_config
import json
import os
import requests
from csirt_langdetect import detect_language
from csirt_masking_data import masking_data, masking_data_with_star

def authenticate_salesforce(username, password, client_id, client_secret):
    # Salesforce authentication endpoint
    auth_url = get_value_from_config('config/config.ini', 'SALESFORCE', 'SF_AUTH_URL')

    # Payload for authentication request
    payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }

    # Send authentication request and get the response
    response = requests.post(auth_url, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to authenticate with Salesforce. Check your credentials.')

def get_salesforce_data(access_token, instance_url, query_string):
    # Salesforce data endpoint
    data_url = f'{instance_url}/services/data/v56.0/query/?q={query_string}'

    # Headers containing the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Send request to retrieve data
    response = requests.get(data_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f'Failed to retrieve data. Status code: {response.status_code}')

def process_salesforce_data(data):
    records = data.get('records', [])
    documents = []
    for record in records:
        # print("Record is ...")
        # print(record)
        # Japanese is not working, although ja_core_news_lg installed
        # record['mssmt__description__c'] = masking_data(record['mssmt__description__c'], language=detect_language(record['mssmt__description__c']))
        # Use openai for faking values (it costs and time)
        # record['mssmt__description__c'] = masking_data(record['mssmt__description__c'], language="en")
        # record['mssmt__description__c'] = masking_data_with_star(record['mssmt__description__c'])
        metadata = {}
        metadata["Type"] = record.get("RecordType", {}).get("DeveloperName")
        metadata["Severity"] = record.get("mssmt__severity__c")
        if metadata["Type"] == 'VulRapid7' :
            print("Rapid 7:",str(record))
        document = Document(
            text = str(record), 
            metadata = metadata,
            metadata_seperator="::",
            metadata_template="{key}=>{value}",
            text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        # print("============================document.text_template==============================================")
        # print(document.text_template)
        # print("==============document.metadata_seperator===============")
        # print(document.metadata_seperator)
        # print("==============document.metadata_template===============")
        # print(document.metadata_template)
        # print("==============document.text===============")
        # print(document.text)
        # print("==============document.get_text()===============")
        # print(document.get_text())
        # print("=============================")
        # print("The ALL sees this: \n", document.get_content(metadata_mode="MetadataMode.ALL"))
        # print("=============================")
        # print("The LLM sees this: \n", document.get_content(metadata_mode="MetadataMode.LLM"))
        # print("=============================")
        # print("The EMBED sees this: \n", document.get_content(metadata_mode="MetadataMode.EMBED"))
        # print("=============================")
        # print("The NONE sees this: \n", document.get_content(metadata_mode="MetadataMode.NONE"))
        # print("==========================================================================")
        documents.append(document)
    return documents

def get_query_string(list_fields, object_name):
    query_fields = ", ".join(list_fields)
    query_string = f"SELECT {query_fields} FROM {object_name}"
    # query_string = query_string + " WHERE Id = 'a0oN000000GYbepIAD'"
    return query_string

def save_data_to_json(data):
    # Save data to a JSON file
    with open('data/salesforce_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    print("Data saved to 'salesforce_data.json'")


def save_data_to_json(data, file_path):
    # Create directories if not exist
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # Convert data to JSON format
    json_data = json.dumps(data, indent=4, ensure_ascii=False)  # indent for pretty formatting

    # Save data to a JSON file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)

    print(f"Data saved to '{file_path}'")
def read_data_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in '{file_path}'.")
    except Exception as e:
        print(f"Error reading data from '{file_path}': {e}")
        return None


def get_json_value(json_string, key):
    try:
        # Parse the JSON string
        json_data = json.loads(json_string)

        # Access the value using the specified key
        value = json_data[key]

        return value
    except Exception as e:
        print(f"Error getting JSON value: {str(e)}")
        return None
def masking_data_in_documents(data_json):
    if isinstance(data_json, dict):
        list_fields_mask = ["Name"]
        for key in data_json.keys():
            # You can customize the fields you want to mask by adding them here
            if key in list_fields_mask:
                data_json[key] = "*****"
            else:
                masking_data_in_documents(data_json[key])
    elif isinstance(data_json, list):
        for item in data_json:
            masking_data_in_documents(item)