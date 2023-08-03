from llama_index import VectorStoreIndex, StorageContext
from llama_index.vector_stores import PGVectorStore


def create_index(database, host, password, port, user, table_name, documents):
    vector_store = PGVectorStore.from_params(
        database=database,
        host=host,
        password=password,
        port=port,
        user=user,
        table_name=table_name,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index