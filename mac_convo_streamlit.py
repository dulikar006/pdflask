from typing import TypedDict, Optional

import requests
from langgraph.graph import StateGraph, END

from clients.openai_client import llm
from vector_db.mongo_db_manager import search_chroma


def run_agents(topic):
    prefix_start = '''
    You will speak in the style of {}, and exaggerate their personality.
    You are in support of {} . You are in a debate with {} over the
     topic: {} . This is the conversation so far \n{}\n. 
    Put forth your next argument to support {} countering {}.\
    Make sure to address all the points made by opposition and try to showcase why people should consider your proposition.
    Dont repeat your previous arguments. 
    Give a comprehensive answer based on below content as your knowledge.
    Never forget to keep your response to 100 words!.
    Keep the conversation going in intense but professional manner.

    [content start here]

    {}

    [content ends]
    '''

    # topic = 'What is the plan for unemployment ?'
    debate_topic = f"""This is a debate on manifestos of two major political parties in Sri Lanka.
                      Debate about: {topic} ?"""

    classes = ["SJB", "NPP"]
    print(classes)

    class GraphState(TypedDict):
        '''
        Classification: To check who should speak next
        History: The conversation so far
        Current_response: Last line spoken by any agent
        Count: Conversation Length
        Results: Verdict by Jury
        Greeting: Welcome message
            '''

        classification: Optional[str] = None
        history: Optional[str] = None
        current_response: Optional[str] = None
        count: Optional[int] = None
        results: Optional[str] = None
        greeting: Optional[str] = None

    def add_message(person, message):
        try:
            response = requests.post("http://localhost:5000/send", json={"person": person, "message": message})
            print(response.json())
        except:
            pass

    def classify(conversation):
        prompt = f'''you are the debate moderator. Your task is to control the debate and decide whoom should speak and when to finish.
        If debate is going out of topic, you should speak up.

        this is the conversation so far: 
        {conversation}

        this is the initial question: {debate_topic}.

        based on that you decide whoom should speak next, whether it is {classes[0]} or {classes[1]} or yourself.
        if its {classes[0]} return {classes[0]}.
        if its {classes[1]} return {classes[1]}.

        Do not intervene always. Only intercept if only necessary. 
        Always check if last last response is off debate topic - {debate_topic}
        If a someone going off topic, please intervene.
        if its you the moderator, return moderator
        Output just the class.
        '''

        # prompt = "classify the sentiment of input as {} or {}. Output just the class. Input:{}".format(
        #     '_'.join(classes[0].split(' ')), '_'.join(classes[1].split(' ')), question)
        response = llm(prompt).strip()
        return response

    def classify_input_node(state):
        '''to close the conversation'''
        if state.get("count") > 6:
            return {"classification": 'moderator'}

        conversation = state.get('history')
        classification = classify(conversation)  # Assume a function that classifies the input
        return {"classification": classification}

    def handle_greeting_node(state):
        argument = {
            "greeting": "Hello! Today we will witness the debate between {} vs {}. Topic today for the debate is {}".format(
                classes[0], classes[1], topic)}
        add_message("Moderator",
                    f"Hello! Today we will witness the debate between {classes[0]} vs {classes[1]}. Topic today for the debate is {topic}")
        return argument

    def load_from_vector(type, debate_topic, current_response):
        if type == "SJB":
            source = 'sjb_blueprint.pdf'
        elif type == "NPP":
            source = 'NPP Presidential Election Manifesto - 2024.pdf'
        else:
            return

        query_prompt = f'''This is a debate on {debate_topic}, 
                            Current response is - {current_response} 
                            generate top 3 key question based on content.
                            only return 3 question'''
        query = llm(query_prompt)

        search_results = search_chroma(query, source=source)
        # search_results_text = "\n".join([doc.page_content for doc in search_results])
        search_results_text = "\n".join([doc.get('content') for doc in search_results])

        return search_results_text

    def handle_pro(state):

        charachter_desc = '''tone in the speech is assertive and confident, reflecting a clear vision for the future of Sri Lanka. He uses a formal and professional style, appropriate for a political debate, with an emphasis on clarity and structure. His language is persuasive, aimed at rallying support for his plans while addressing economic challenges candidly. He balances optimism about potential growth with realism about the current economic situation, creating a tone that is both hopeful and pragmatic. Overall, he seeks to inspire trust and engagement among his audience'''

        summary = state.get('history', '').strip()
        current_response = state.get('current_response', '').strip()
        if summary == 'Nothing':
            data = load_from_vector(classes[0], debate_topic, current_response)
            prompt = prefix_start.format(charachter_desc, classes[0], classes[1], debate_topic, 'Nothing', classes[0],
                                         "Nothing", data)
            argument = classes[0] + ":" + llm(prompt)
            add_message("SJB", argument)
            # print(classes[0] + ":" + argument)
            summary = 'START\n'
        else:
            data = load_from_vector(classes[0], debate_topic, current_response)
            prompt = prefix_start.format(charachter_desc, classes[0], classes[1], debate_topic, summary, classes[0],
                                         current_response,
                                         data)
            argument = classes[0] + ":" + llm(prompt)
            add_message("SJB", argument)
            # print(classes[0] + ":" + argument)
        return {"history": summary + '\n' + argument, "current_response": argument, "count": state.get('count') + 1}

    def handle_opp(state):

        charachter_desc = '''tone of speech is assertive and urgent, reflecting a critical stance on current political failures. He speaks passionately and candidly about the need for accountability and reform, aiming to inspire action while conveying hope for a better future in Sri Lanka through transparency and integrity.'''

        summary = state.get('history', '').strip()
        current_response = state.get('current_response', '').strip()

        data = load_from_vector(classes[1], debate_topic, current_response)

        prompt = prefix_start.format(charachter_desc, classes[1], classes[0], debate_topic, summary, classes[1],
                                     current_response, data)
        argument = classes[1] + ":" + llm(prompt)
        # print(classes[0] + ":" + argument)
        add_message("NPP", argument)
        return {"history": summary + '\n' + argument, "current_response": argument, "count": state.get('count') + 1}

    def handle_moderator(state):
        '''to close the conversation'''
        if state.get("count") > 6:
            moderator_prefix_start = """
                debate topic : {}
                You are the debate moderator.
                Speak directly to the candidates: {}, {}.
                Ask them to close the debate with final consolidated statements for topic. 
                Do not add anything else.
                Try to bring conversation into a closure.
                debate topic: {}
                summary so far: {}
                current response: {}"""

        else:
            moderator_prefix_start = """
            debate topic : {}
            You are the debate moderator.
            Please make the debate topic more specific. 
            Frame the debate topic as a problem to be solved.
            Be creative and imaginative.
            Please reply with the specified topic in 50 words or less. 
            Speak directly to the presidential candidates: {}, {}.
            Do not add anything else.
            Try to bring conversation into a closure.
            debate topic: {}
            summary so far: {}
            current response: {}"""

        summary = state.get('history', '').strip()
        current_response = state.get('current_response', '').strip()

        prompt = moderator_prefix_start.format(debate_topic, classes[1], classes[0], debate_topic, summary,
                                               current_response)
        argument = classes[1] + ":" + llm(prompt)
        # print(classes[0] + ":" + argument)
        add_message("Moderator", argument)
        return {"history": summary + '\n' + argument, "current_response": argument, "count": state.get('count') + 1}

    def result(state):
        summary = state.get('history').strip()
        prompt = "Summarize the conversation and judge who won the debate.No ties are allowed. Conversation:{}".format(
            summary)
        return {"results": llm(prompt)}

    def decide_next_node(state):
        if state.get('classification') == '_'.join(classes[0].split(' ')):
            return "handle_pro"
        elif state.get('classification') == '_'.join(classes[1].split(' ')):
            return "handle_opp"
        else:
            return "handle_moderator"

    def check_conv_length(state):
        return "result" if state.get("count") >= 10 else "classify_input"

    workflow = StateGraph(GraphState)

    workflow.add_node("classify_input", classify_input_node)
    workflow.add_node("handle_greeting", handle_greeting_node)
    workflow.add_node("handle_pro", handle_pro)
    workflow.add_node("handle_opp", handle_opp)
    workflow.add_node("handle_moderator", handle_moderator)
    workflow.add_node("result", result)

    # -----------------------------------------------------------

    ''''1st edge: Once the speaker for last conversation is recognized using classify_input_node, choose the alternate speaker
    2nd & 3rd edge basically introduces a cycle where if the conversation limit is not reached, go to other speaker else to the jury'''

    workflow.add_conditional_edges(
        "classify_input",
        decide_next_node,
        {
            "handle_pro": "handle_pro",
            "handle_opp": "handle_opp",
            "handle_moderator": "handle_moderator"
        }
    )

    workflow.add_conditional_edges(
        "handle_pro",
        check_conv_length,
        {
            "result": "result",
            "classify_input": "classify_input"
        }
    )

    workflow.add_conditional_edges(
        "handle_opp",
        check_conv_length,
        {
            "result": "result",
            "classify_input": "classify_input"
        }
    )

    workflow.add_conditional_edges(
        "handle_moderator",
        check_conv_length,
        {
            "result": "result",
            "classify_input": "classify_input"
        }
    )

    '''Adding graph entry point and remaining definite edges'''

    workflow.set_entry_point("handle_greeting")
    workflow.add_edge('handle_greeting', "handle_pro")
    workflow.add_edge('result', END)

    '''Compiling graph and starting debate'''
    app = workflow.compile()

    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    conversation = app.invoke({'count': 0, 'history': 'Nothing', 'current_response': ''})
    # print(conversation['history'])
    #
    # print(conversation["result"])
# run_agents('Education')
