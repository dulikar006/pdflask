import os

from pymongo import MongoClient
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_openai import AzureOpenAIEmbeddings
from pymongo.operations import SearchIndexModel

#https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/langchain/
class MongoDBClient:

    def __init__(self, db_name="langchain_db", collection_name="presidential_campaign"):
        self.url = os.environ['mongo_url']
        self.vector_store = None
        self.atlas_collection = None
        self.db_name = db_name
        self.collection_name = collection_name
        self.vector_search_index = "vector_index"

    def client_connection(self):
        client = MongoClient(self.url)
        return client[self.db_name][self.collection_name]

    def connect(self):
        client = MongoClient(self.url)
        # Define collection and index name

        self.atlas_collection = client[self.db_name][self.collection_name]

        embeddings = AzureOpenAIEmbeddings(
            # dimensions: Optional[int] = None, # Can specify dimensions with new text-embedding-3 models
            azure_endpoint=os.environ['embed_endpoint'],
            api_key=os.environ['embed_key'],
            openai_api_version='2023-05-15',
            azure_deployment='text-embedding-ada-002'
        )

        self.vector_store = MongoDBAtlasVectorSearch(
            embedding=embeddings,
            collection=self.atlas_collection,
            index_name=self.vector_search_index
        )

    def create_index(self):
        # Create your index model, then create the search index
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1536,
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "page"
                    }
                ]
            },
            name=self.vector_search_index,
            type="vectorSearch"
        )
        self.atlas_collection.create_search_index(model=search_index_model)

    def add_documents(self, documents, ids):
        self.vector_store.add_documents(documents=documents, ids=ids)

    def delete_documents(self, ids_list: [str]):
        self.vector_store.delete(ids=ids_list)

    def search(self, query):
        results = self.vector_store.similarity_search(query=query, k=5)
        return [{'content': doc.page_content, 'metadata': doc.metadata} for doc in results]

    def search_with_filter(self, query, filter: [dict]):
        results = self.vector_store.similarity_search(query=query, k=5, post_filter=[filter])
        return [{'content': doc.page_content, 'metadata': doc.metadata} for doc in results]

    def search_with_score(self, query):
        results = self.vector_store.similarity_search_with_score(query=query, k=1)
        output = []
        for doc, score in results:
            output.append({'content': doc.page_content, 'score': score, 'metadata': doc.metadata})
        return output

    def lang_retriever(self, query):
        retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 1, "fetch_k": 2, "lambda_mult": 0.5},
        )
        return retriever.invoke(query)
