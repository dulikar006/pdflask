sections = '''
    Content:
    [CONTENT]
    {article}
    [END OF CONTENT]
    
    An article is broken down into multiple sub-documents. Above is just one sub-document of an article.
    
    Your task is to perform the following steps to analyse the content identify the subject and generate key points related to the subject.
    
    [STEPS]
    
    step 1. Break the content down into smaller sections based on sub-topics, themes, areas of discussion, field of interest, sector, segment etc.
    step 2. Review identified sections and ensure there are no gaps between each section.
    step 3. Check if section is describing about any extraneous content such as disclaimer, appendix, copyright, disclosure and id any, remove them.
    step 4. Remove Non-relevant Advisory content.
    step 5. Identify key-points such as informative entities, key arguments, main topics, key entities, information, figure, events, cause, impacts etc. in each section.
    step 6. Review the identified key points and check if any additional entities, arguments or topics have been overlooked.
    step 7. Provide Impact analysis for each section based on the key points and relationship, showcasing positive, negative, neutral or compound impacts.
    step 8. Provide sentiment intensity analysis score between -100 and +100 based on the tone, lexicon, ratio of positive or negative.
    step 9. Based on the subject which is {subject}, identify the category this section false into from top 100 categories under the {subject}.
    step 10. provide an explanation of the identified category , explaining why it false under that category.
    step 11. Check  if the final section generated, cover all the context mentioned in the content. If not repeat from step 1 again.
    
    [END OF STEPS]
    
    [GUIDELINES]
    - Do not include any misleading information and avoid any hallucinations.
    - Don not mockup any explanation and elaboration.
    - Include relevant details, examples and elaboration using context truly present in the provided content.
    - The section generation should solely be based on the knowledge extracted from the content.
    - Keep impact category to only positive, negative, neutral or compound.
    - Be more specific with the year when mentioning date reference, if you have the details.
    - Include complete details. e.g. number for each key point identified.
    [END OF GUIDELINES]
    
    Format the output as JSON with the following structure:
    KeypointSections: [
        [
        Section: [insert section name here],
        Impact: [Impact category],
        SentimentScore: [Sentiment score between -100 and +100],
        Category: [insert category name],
        KeyPoints: [[key point], [key point], [key point], [key point], [key point], [key point] ...]
        ],
        [
        Section: [insert section name here],
        Impact: [Impact category],
        SentimentScore: [Sentiment score between -100 and +100],
        Category: [insert category name],
        KeyPoints: [[key point], [key point], [key point], [key point], [key point], [key point] ...]
        ],
        ...]
        
'''