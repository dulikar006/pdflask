import json

from clients.openai_client import call_openai
from utils.propmts import sections


def generate_metadata(doc: str) -> list:

    try:

        json_string = call_openai(sections, {'article': doc, 'subject': 'election manifesto'})

        first_brace_index = json_string.find('{')
        last_brace_index = json_string.rfind('}')
        extracted_json = json_string[first_brace_index:last_brace_index + 1]
        extracted_json = extracted_json.replace("'", '"')
        result_dict = json.loads(extracted_json)

        return result_dict.get('KeypointSections')
    except:
        pass
