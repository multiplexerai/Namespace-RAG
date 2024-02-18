import csv
import json
from typing import List

async def generic_query(query_text: str, namespace_prefix: str):
    namespaces = [f'{namespace_prefix}n', f'{namespace_prefix}q', f'{namespace_prefix}s']
    all_matches_for_logging = []
    for namespace in namespaces:
        matches = await query(query_text, namespace, top_k=3)
        all_matches_for_logging.extend(matches)
    combined_matches_text = " ".join(all_matches_for_logging)
    prompt = f"In the following data, find the relevant info to answer: {query_text}\n{combined_matches_text}"
    response = await get_gpt_response(prompt)
    log_file = f"{namespace_prefix}_query_response_log.csv"
    with open(log_file, 'a', newline='', encoding='utf-8') as log_file:
        writer = csv.writer(log_file)
        writer.writerow([prompt, response])
    return {"response": response}

async def query(query_text: str, namespace: str, top_k=2):
    response = await client.embeddings.create(input=[query_text], model='your_model_here')  # Specify your model
    xq = response.data[0].embedding
    res = index.query([xq], top_k=top_k, include_metadata=True, namespace=namespace)
    matches_list = [match['metadata']['text'] for match in res['matches']]
    return matches_list

async def get_gpt_response(prompt):
    system_message = {"role": "system", "content": "Please provide a concise and accurate answer based on the information provided."}
    messages = [system_message, {"role": "user", "content": prompt}]

    response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Adjust the model as needed
                    messages=messages,
                    temperature=0.4,
                    max_tokens=300
                )
    if response is None:
        return "GPT API request timed out"
    
    assistant_message = response.choices[0].message.content
        
    return assistant_message
