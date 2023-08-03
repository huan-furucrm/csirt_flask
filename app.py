import json
import math
from flask import Flask, request
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from csirt_config_info import (
    get_value_from_config,
    get_openai_config,
    get_salesforce_config,
    get_postgresql_config
)
from csirt_salesforce import (
    authenticate_salesforce,
    get_salesforce_data,
    process_salesforce_data,
    get_query_string,
    save_data_to_json,
    read_data_from_json,
    masking_data_in_documents
)
from csirt_postgresql import (
    create_conn,
    close_conn,
    get_postgresql_query_data,
    build_postgresql_query_string,
    convert_data_to_nparray,
    get_postgresql_table_name,
    get_postgresql_fields,
    get_postgresql_condition,
    get_data_from_postgresql
)
from csirt_index import create_index
from csirt_user_query import (
    set_user_query, 
    get_embeddings, 
    get_top1_similar_docs,
    get_top2_similar_docs,
    get_tops_similar_docs,
    get_query_index)
from csirt_suggest_next_action import ask_GPT
from csirt_masking_data import masking_data
from csirt_langdetect import detect_language

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World!!!"


@app.route('/create-index')
def csirt_create_index():
    print("Run started...")
    # Salesforce credentials
    print("Get salesforce config...")
    sf_config = get_salesforce_config()

    print("Get postgresql config...")
    # Postgresql credentials
    postgre_config = get_postgresql_config()
    postgre_table_name = get_postgresql_table_name()

    print("Set list fields...")
    list_fields = ["Id", "Name", "mssmt__description__c"]
    list_fields.append("mssmt__severity__c")
    list_fields.append("RecordType.DeveloperName")
    list_fields.append(
        "(select+mssmt__Subject__c,mssmt__TicketId__c,mssmt__description__c,LastModifiedDate,mssmt__Priority__c+from+mssmt__VulnerableTodoOfTicket__r+order+by+LastModifiedDate+asc)")
    list_fields.append(
        "(select+mssmt__Content__c,LastModifiedDate+from mssmt__Vulnerability_Note__r+order+by+LastModifiedDate+asc)")
    try:
        # Fetch data from Salesforce
        # Authenticate with Salesforce
        print("Get salesforce token...")
        auth_response = authenticate_salesforce(
            sf_config.get('sf_user'),
            sf_config.get('sf_passwd'),
            sf_config.get('sf_client_id'),
            sf_config.get('sf_client_secret'))
        access_token = auth_response['access_token']
        instance_url = auth_response['instance_url']
        object_name = 'mssmt__MSS_VulSubTicket__c'
        print("Get salesforce query string...")
        query_string = get_query_string(list_fields, object_name)
        print("Get salesforce data...")
        data = get_salesforce_data(access_token, instance_url, query_string)
        # print("Masking datas...")
        
        # masking_data_in_documents(data)
        print("process salesforce data...")
        documents = process_salesforce_data(data)
        print("documets is ....")
        print(documents)
        print("Start create table and index.")
        index = create_index(
            database=postgre_config.get('postgre_database'),
            host=postgre_config.get('postgre_host'),
            password=postgre_config.get('postgre_passwd'),
            port=postgre_config.get('postgre_port'),
            user=postgre_config.get('postgre_user'),
            table_name=postgre_table_name,
            documents=documents
        )
        index.vector_store.query
        print("Finish create table and index.")
        return "OK"
    except Exception as e:
        print(f'Error: {e}')
        return "Failed"
    
# @app.route('/create-query-index')
def csirt_create_query_index(id_value):
    try:
        sf_config = get_salesforce_config()
        list_fields = ["Id", "Name", "mssmt__description__c"]
        list_fields.append("mssmt__severity__c")
        list_fields.append("RecordType.DeveloperName")
        list_fields.append(
            "(select+mssmt__Subject__c,mssmt__TicketId__c,mssmt__description__c,LastModifiedDate,mssmt__Priority__c+from+mssmt__VulnerableTodoOfTicket__r+order+by+LastModifiedDate+asc)")
        list_fields.append(
            "(select+mssmt__Content__c,LastModifiedDate+from mssmt__Vulnerability_Note__r+order+by+LastModifiedDate+asc)")
        auth_response = authenticate_salesforce(
            sf_config.get('sf_user'),
            sf_config.get('sf_passwd'),
            sf_config.get('sf_client_id'),
            sf_config.get('sf_client_secret'))
        access_token = auth_response['access_token']
        instance_url = auth_response['instance_url']
        object_name = 'mssmt__MSS_VulSubTicket__c'
        query_string = get_query_string(list_fields, object_name)
        query_string = query_string + " WHERE Id = '" + id_value + "'"
        data = get_salesforce_data(access_token, instance_url, query_string)
        documents = process_salesforce_data(data)
        
        # Postgresql credentials
        postgre_config = get_postgresql_config()
        postgre_table_name = get_postgresql_table_name()
        postgre_conn = create_conn(
            database=postgre_config.get('postgre_database'),
            user=postgre_config.get('postgre_user'),
            password=postgre_config.get('postgre_passwd'),
            host=postgre_config.get('postgre_host'),
            port=postgre_config.get('postgre_port')
        )
        
        register_vector(postgre_conn)
        cur = postgre_conn.cursor()
        # Get the top 1 most similar documents using the KNN <=> operator
        cur.execute("DROP TABLE IF EXISTS tsdb.public.data_salesforce_data_index_query;")
        postgre_conn.commit()
        index = create_index(
            database=postgre_config.get('postgre_database'),
            host=postgre_config.get('postgre_host'),
            password=postgre_config.get('postgre_passwd'),
            port=postgre_config.get('postgre_port'),
            user=postgre_config.get('postgre_user'),
            table_name=postgre_table_name+"_query",
            documents=documents
        )
        print("===================vector_store==================================")
        print(index.vector_store)
        query_index = get_query_index(postgre_conn)
        query_result = list(query_index)
        dbb = query_result[0]
        str_results = str(dbb.tolist())
        return str_results
    except Exception as e:
        print(f'Error: {e}')
        return "Failed"


@app.route('/query', methods=['POST'])
def csirt_query():
    print("Get description parameters...")
    data = request.json
    description = data.get('description')
    index = description.find("'Id': '")
    end_quote = description.find("'", index +8)
    id_value = description[index + 7:end_quote]
    print("===================id_value===============================")
    print(id_value)
    print("====================================================")
    output = ''
    output = output + "Get description parameters..." + "<br />"
    output = output + description + "<br />"
    try:
        print("Get postgresql config...")
        output = output + "Get postgresql config..." + "<br />"
        # Postgresql credentials
        postgre_config = get_postgresql_config()
        postgre_table_name = get_postgresql_table_name()
        postgre_fields = get_postgresql_fields()
        postgre_condition = get_postgresql_condition()
        postgre_conn = create_conn(
            database=postgre_config.get('postgre_database'),
            user=postgre_config.get('postgre_user'),
            password=postgre_config.get('postgre_passwd'),
            host=postgre_config.get('postgre_host'),
            port=postgre_config.get('postgre_port')
        )

        register_vector(postgre_conn)
        postgre_cur = postgre_conn.cursor()
        # postgre_query_string = build_postgresql_query_string(table_name=get_postgresql_table_name(), fields=get_postgresql_fields(), condition=get_postgresql_condition())
        postgre_query_string = "SELECT COUNT(*) as cnt FROM data_" + get_postgresql_table_name() + ";"
        postgre_cur.execute(postgre_query_string)
        num_records = postgre_cur.fetchone()[0]
        print("Number of vector records in table: ", num_records, "\n")
        output = output + "Number of vector records in table: " + str(num_records) + "<br />"

        # # print the first record in the table, for sanity-checking
        # postgre_query_sanity_checking = "SELECT * FROM data_" + get_postgresql_table_name() + " LIMIT 1;"
        # postgre_cur.execute(postgre_query_sanity_checking)
        # records = postgre_cur.fetchall()
        # print("First record in table: ", records)
        # output = output + "First record in table: " + str(records) + "<br />"

        # Create an index on the data for faster retrieval
        print("Create an index on the data for faster retrieval.")
        output = output + "Create an index on the data for faster retrieval." + "<br />"
        # calculate the index parameters according to best practices
        num_lists = num_records / 1000
        if num_lists < 10:
            num_lists = 10
        if num_records > 1000000:
            num_lists = math.sqrt(num_records)

        # use the cosine distance measure, which is what we'll later use for querying
        postgre_cur.execute(
            f'CREATE INDEX ON data_{get_postgresql_table_name()} USING ivfflat (embedding vector_cosine_ops) WITH (lists = {num_lists});')
        postgre_conn.commit()
        print("Finish create an index on the data for faster retrieval.")
        output = output + "Finish create an index on the data for faster retrieval." + "<br />"

        # Define a question you want to answer
        input_text = 'リモートの Windows ホストにインストールされている Microsoft Edge のバージョンは、108.0.1462.54 より前です。したがって、2022 年 12 月 16 日のアドバイザリに記載されている複数の脆弱性の影響を受けます。'
        if len(description) > 0:
            input_text = description
        print("input_text is ...")
        output = output + "input_text is ..." + input_text + "<br />"
        # set_user_query(input_text)
        print("Start embedding input query...")
        output = output + "Start embedding input query..." + "<br />"
        # initialize sentence transformer model
        # model = SentenceTransformer('sangmini/msmarco-cotmae-MiniLM-L12_en-ko-ja')
        embedding_query = csirt_create_query_index(id_value)
        print("Start query database...")
        output = output + "Start query database..." + "<br />"
        # query_results = get_top1_similar_docs(embedding_query, postgre_conn)
        query_results = get_tops_similar_docs(query_embedding=embedding_query, conn=postgre_conn, top=4)
        results = json.dumps(query_results, ensure_ascii=False)
        print("Query results...")

        output = output + "Query results..." + "<br />"
        print(query_results)
        output = output + "Get id from referenced tickets..." + "<br />"
        referenced_records = []
        for result in query_results:
            if result[0].find("'Id': '") != -1:
                start_position = result[0].find("'Id': '") + len("'Id': '")
                end_position = result[0].find("'", start_position)
                referenced_records.append(result[0][start_position:end_position])
        print(referenced_records)
        
        print("Start close connection.")
        output = output + "Start close connection." + "<br />"
        close_conn(postgre_conn)
        print("Finish close connection.")
        output = output + "Finish close connection." + "<br />"

        print("Ask chatGPT...")
        output = output + "Ask chatGPT..." + "<br />"
        response = ask_GPT(query_results, input_text)
        response_json = {"gpt_answer": response, "referenced_record": referenced_records}
        output_json = {"output": str(output), "response": str(response)}
        output_dumps = json.dumps(output_json, ensure_ascii=False)
        print("OUTPUT:", output_json.get("response"))
        # if DEBUG then return output_dumps, if run then return response
        return output_dumps
    except Exception as e:
        print(f'Error: {e}')
        return "Failed"


if __name__ == '__main__':
    app.run(debug=True)