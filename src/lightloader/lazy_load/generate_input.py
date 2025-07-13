import openai
import os
import json

# Define global variables for base_url and llm model
BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"
prompt_path = './prompt/generate_user_input'

def _generate(handler_path: str, prompt_path: str, api_key: str, output_path: str, prompt_content :str):

    # Read the handler function content
    with open(handler_path, 'r') as f:
        handler_content = f.read()

    # Replace the placeholder in the prompt with the handler function content
    final_prompt = prompt_content.replace('{handler_function}', handler_content)

    client = openai.OpenAI(
        api_key=api_key,
        base_url=BASE_URL,
    )
    
    system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

EXAMPLE INPUT: 
Which is the highest mountain in the world? Mount Everest.

EXAMPLE JSON OUTPUT:
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""
    user_prompt = final_prompt
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )
    
    output_json = response.choices[0].message.content 

    try:
    # Parse the JSON string
        output = json.loads(output_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Original JSON string: {output_json}")
        # Read the default.json content if parsing fails
        with open('default.json', 'r') as default_file:
            output = json.load(default_file)

    # Extract the function calls from the 'function_calls' key
    function_calls = output.get('function_calls', [])

    # Create a copy of the handler file
    os.system(f'cp {handler_path} {output_path}')

    # Append the generated function calls to the copied handler file
    with open(output_path, 'a') as f:
        for call in function_calls:
            f.write(f'\n\n{call}')


def generate_user_input(handler_path: str, output_path: str):
    with open('api_key') as f:
        api_key = f.read()
    
    with open(prompt_path, 'r') as f:
        prompt_content = f.read()

    _generate(handler_path, prompt_path, api_key, output_path,prompt_content)