import os
from litellm import completion
from openai import OpenAIError
import json


def load_prompt(version="v1"):
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "classifier", f"{version}.txt")
    with open(prompt_path, "r") as f:
        return f.read()

def classify_article(article, prompt_version="v1"):
    """
    Classifies an article as relevant or irrelevant using an LLM and a versioned prompt.
    Args:
        article (dict): The article to classify.
        prompt_version (str): The version of the prompt to use.
    Returns:
        bool: True if relevant, False if irrelevant.
    """
    prompt = load_prompt(prompt_version)
    
    try :
        response = completion(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, 
                    {"role": "user", "content": f"Classify this article:\n\nTitle: {article['title']}\n\nBody: {article['body']}"}],
            temperature=0.0
        )
        
        if response and response.choices:
            content = response.choices[0].message.content.strip()
            json_content = json.loads(content)

            if "relevant" in json_content and "summary" in json_content:
                return {
                    "relevant": json_content["relevant"],
                    "summary": json_content["summary"]
                }
            else:
                print(f"Unexpected response format: {content}")
                return False
        else:
            print("No valid response from LLM.")
            return False
    except OpenAIError as e:
        print(f"Error during LLM completion: {e}")
        return False

# Example usage:
# result = classify_article(article, prompt_version="v1", llm_client=my_llm)