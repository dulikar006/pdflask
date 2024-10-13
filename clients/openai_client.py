import logging
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)



def call_openai(base_prompt, input):
    try:

        llm = AzureChatOpenAI(
            azure_endpoint=os.environ['openai_endpoint'],
            api_key=os.environ['openai_key'],
            openai_api_version='2023-03-15-preview',
            model='GPT_4o'
        )

        prompt = PromptTemplate(
            input_variables=list(input.keys()),
            template=base_prompt)

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        result = chain.invoke(input)

        # log = {'input': input, 'output': result}

        return result
    except Exception as err:
        logger.error(f'Error Calling Open AI API - Error: {err}')

def get_llm():
    llm = AzureChatOpenAI(
        azure_endpoint=os.environ['openai_endpoint'],
        api_key=os.environ['openai_key'],
        openai_api_version='2023-03-15-preview',
        model='GPT_4o'
    )
    return llm

def llm(input_text):
    # Initialize Azure OpenAI LLM
    llm = AzureChatOpenAI(
        azure_endpoint=os.environ['openai_endpoint'],
        api_key=os.environ['openai_key'],
        openai_api_version='2023-03-15-preview',
        model='GPT_4o'
    )

    # Define a prompt using the input text
    prompt = PromptTemplate.from_template("{input_text}")

    # Create the LLM chain with prompt and output parsing
    output_parser = StrOutputParser()
    chain = llm | output_parser
    result = chain.invoke(input_text)
    return result
