import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from clients.mongo_client import MongoDBClient
from presidential_debate_flask.pdflask.vector_db.process_input_data import generate_metadata


def upload_file(file_name):
    try:
        # db = PostgresDB()
        # db.connect()

        mc = MongoDBClient()
        mc.connect()

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

                    # db.insert("metadata", list(metadata_dict.keys()), list(metadata_dict.values()))

                    metadata_dict.pop('KeyPoints')

                    custom_doc = Document(
                        page_content=page_content,  # The text content of the document chunk
                        metadata=metadata_dict
                    )
                    custom_documents.append(custom_doc)

        # Generate UUIDs for the documents
        uuid_list = [str(uuid.uuid4()) for _ in range(len(split_docs))]

        # Add documents to MongoDB
        mc.add_documents(split_docs, uuid_list)

        return uuid_list  # Return the list of generated UUIDs
    except Exception as err:
        print(f"Error while uploading documents to MongoDB - {err}")
        return False


def search_chroma( query, source=None, category=None, top_k=5):
    mc = MongoDBClient()
    mc.connect()
    if source:
        search_results = mc.search_with_filter(query, {"source": source})
    else:
        search_results = mc.search(query)

    return search_results


# upload_file('sjb_blueprint.pdf')
# upload_file('NPP Presidential Election Manifesto - 2024.pdf')
#
# query = 'How does the SJB plan to achieve sustainable development and inclusive progress while leveraging innovation for long-term prosperity?'
#
# query = "economy"
#
# # result = search_chroma(query, source='sjb_blueprint.pdf')
# result = search_chroma(query)
# print(result)
