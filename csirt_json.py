from llama_index import Document, download_loader, StorageContext, VectorStoreIndex
from pathlib import Path
import json
import numpy as np
import os
def convert_json_to_document(file_path, document_id):
    documents = []
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        # Create a document object
        document = Document(
            id_=document_id,
            text=json.dumps(json_data),
            metadata={'file_name': file_path}
        )
        documents.append(document)

    except Exception as e:
        print(f"Error converting JSON to document: {str(e)}")
    return documents

def process_files_in_folder(folder_path):
    # Init documents
    documents = []

    # Check if the folder path exists
    if not Path(folder_path).is_dir():
        print("Folder path does not exist.")
    else:
        # Loop through all the files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if the current item is a file (not a subdirectory)
            if os.path.isfile(file_path):
                _, file_extension = os.path.splitext(filename)
                file_extension = file_extension.lower()

                if file_extension == '.txt':
                    print(f"Processing {filename}:")

                elif file_extension == '.json':
                    print(f"Processing {filename}:")
                    documents_json = convert_json_to_document(file_path, filename)

                    documents = documents + documents_json

                elif file_extension == '.csv':
                    print(f"Processing {filename}:")
                    PandasCSVReader = download_loader("PandasCSVReader")

                    loader = PandasCSVReader()
                    documents_csv = loader.load_data(file=Path(file_path))
                    documents = documents + documents_csv

                elif file_extension == '.pdf':
                    print(f"Processing {filename}:")
                    CJKPDFReader = download_loader("CJKPDFReader")

                    loader = CJKPDFReader()
                    documents_pdf = loader.load_data(file=Path(file_path))
                    documents = documents + documents_pdf
                    # Perform your processing using the 'pdf_reader' object
                    # Replace the print statement with your desired action

                elif file_extension in ['.xml', '.html']:
                    print(f"Processing {filename}:")
                    # Perform your processing on the 'content' variable
                    # Replace the print statement with your desired action

            else:
                print(f"Skipping {filename}: Unsupported file type")

    print(documents)
    return documents
def convert_data_to_nparray(data):
    list_data = []
    for data_item in data:
        vector_str = json.loads(data_item[0])
        np_array = np.array(vector_str)
        list_data.append(np_array)
    return np.array(list_data)