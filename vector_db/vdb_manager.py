import uuid

from clients.postgres_client import PostgresDB
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from vector_db.process_input_data import generate_metadata


class UploadFilesVDB:

    def __init__(self):
        self.vectorstore = None

    def connect(self):
        self.vectorstore = Chroma(
            collection_name="rag-chroma",
            persist_directory=PERSIST_DIR,
            embedding_function=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        )

    def create_chroma(self, file_name):

        '''Function to create a Chroma vector store from documents'''

        db = PostgresDB()
        db.connect()

        loader = PyPDFLoader(file_name)
        pages = loader.load_and_split()

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=400, chunk_overlap=20
        )

        split_docs = text_splitter.split_documents(pages)

        custom_documents = []
        i = 0
        for idx, doc in enumerate(split_docs):

            i += 1
            if i > 10:
                break

            sections = generate_metadata(doc.page_content)

            if isinstance(sections, list):
                for section_doc in sections:
                    page_content = " /n ".join(section_doc.get('KeyPoints'))

                    metadata_dict = doc.metadata.copy()

                    metadata_dict.update(section_doc)

                    '''update metdata in db'''
                    metadata_dict['id'] = str(uuid.uuid4())

                    db.insert("metadata", list(metadata_dict.keys()), list(metadata_dict.values()))

                    metadata_dict.pop('KeyPoints')

                    custom_doc = Document(
                        page_content=page_content,  # The text content of the document chunk
                        metadata=metadata_dict
                    )
                    custom_documents.append(custom_doc)

        vectorstore = Chroma.from_documents(
            documents=custom_documents,
            collection_name="rag-chroma",
            # embedding=AzureOpenAIEmbeddings(model="text-embedding-3-large",
            #                                 api_key='9cae1c98f81247a7a02c8e0b3c2bee76',
            #                                 openai_api_version='2024-02-15-preview',
            #                                 azure_endpoint="https://mcap-eus-mts-ark-openai.openai.azure.com/openai/deployments/GPT_4o/chat/completions?api-version=2024-02-15-preview"
            #                                 ),
            embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
            persist_directory="./.chroma",
        )

        db.disconnect()

        # vectorstore.persist()  # Persist the vector store for future use

    def update_chroma(self, file_name):
        db = PostgresDB(user="myuser", password="mypassword", host="localhost", port="5432",
                        dbname="mydatabase")
        db.connect()

        loader = PyPDFLoader(file_name)
        pages = loader.load_and_split()

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=400, chunk_overlap=20
        )

        split_docs = text_splitter.split_documents(pages)

        custom_documents = []
        i = 0
        for idx, doc in enumerate(split_docs):

            i += 1
            # if i > 10:
            #     break

            sections = generate_metadata(doc.page_content)

            if isinstance(sections, list):
                for section_doc in sections:

                    try:
                        page_content = " /n ".join(section_doc.get('KeyPoints'))

                        metadata_dict = doc.metadata.copy()

                        metadata_dict.update(section_doc)

                        '''update metdata in db'''
                        metadata_dict['id'] = str(uuid.uuid4())

                        db.insert("metadata", list(metadata_dict.keys()), list(metadata_dict.values()))

                        metadata_dict.pop('KeyPoints')

                        custom_doc = Document(
                            page_content=page_content,  # The text content of the document chunk
                            metadata=metadata_dict
                        )
                        custom_documents.append(custom_doc)
                    except:
                        pass

        self.connect()
        self.vectorstore.add_documents(custom_documents)
        print("documents added")
        # vectorstore.persist()  # Save the updated store

    def search_chroma(self, query, source=None, category=None, top_k=5):
        '''Load the existing vector store'''

        # name_list = ['doc1', 'doc2', 'doc3']
        source_list = [source]
        category_list = [category]

        # Create filter dictionaries for each list
        # name_filter = {"name": {"$in": name_list}}
        source_filter = {"source": {"$in": source_list}}
        category_filter = {"Category": {"$in": category_list}}

        # Combine filters using $and or $or operators
        combined_filter = {
            "$and": [
                # name_filter,
                source_filter
                # category_filter
            ]
        }

        # base_retriever = self.vectorstore.as_retriever(search_kwargs={'k': top_k})
        # # Create the retriever with the combined filter
        # if source_filter:
        base_retriever = self.vectorstore.as_retriever(search_kwargs={'k': top_k, 'filter': source_filter})

        # Perform the query
        search_results = base_retriever.invoke(query)

        return search_results


# ufvdb = UploadFilesVDB()
# ufvdb.create_chroma('sjb_blueprint.pdf')
# ufvdb.update_chroma('sjb_blueprint.pdf')
# ufvdb.update_chroma('NPP Presidential Election Manifesto - 2024.pdf')


# ufvdb = UploadFilesVDB()
# ufvdb.connect()
# result = ufvdb.search_chroma('How does the SJB plan to achieve sustainable development and inclusive progress while leveraging innovation for long-term prosperity?', source='sjb_blueprint.pdf')
# print(result)
