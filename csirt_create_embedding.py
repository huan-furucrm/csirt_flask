from sentence_transformers import SentenceTransformer

# initialize sentence transformer model
model = SentenceTransformer('sangmini/msmarco-cotmae-MiniLM-L12_en-ko-ja')
input_text = {'attributes': {'type': 'mssmt__MSS_VulSubTicket__c', 'url': '/services/data/v56.0/sobjects/mssmt__MSS_VulSubTicket__c/a0oN000000GYbepIAD'}, 'Id': 'a0oN000000GYbepIAD', 'Name': 'VT-00000358', 'mssmt__description__c': 'Jenkins Advisory 2023-07-26: CVE-2023-39153: CSRF vulnerability in GitLab Authentication Plugin', 'mssmt__severity__c': 'Medium', 'RecordType': {'attributes': {'type': 'RecordType', 'url': '/services/data/v56.0/sobjects/RecordType/012N0000003sdEXIAY'}, 'DeveloperName': 'VulRapid7'}, 'mssmt__VulnerableTodoOfTicket__r': None, 'mssmt__Vulnerability_Note__r': None}
embedding_query = model.encode(str(input_text))

print(str(embedding_query.tolist()))