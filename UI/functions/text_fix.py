import requests
import os
from dotenv import load_dotenv 

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env file. Please add PERPLEXITY_API_KEY to your .env file.")

BASE_URL = "https://api.perplexity.ai"

def generate_sentences(input_text):
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    
    payload = {
    "model": "llama-3.1-sonar-small-128k-online",  
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a specialized AI assistant for correcting text input. "
                "Your task is to correct grammar, punctuation, and spacing errors in the provided input. "
                "Do not add, translate, rephrase, or modify any part of the input beyond necessary corrections. "
                "Do not explain your corrections, include extra text, or change the structure of the input unnecessarily. "
                "If no corrections are needed, return the input text exactly as it is, without any changes."
                "Only output the corrected text and no extra information about the corrections or for the corrections."
                "Do not give information about the words or the context of the input."
                "If there is a single word in the input, give the word in its correct form without adding anything else"
                "If there are multiple words, separate them with spaces and give them in the correct order."
            )
        },
        {
            "role": "user",
            "content": input_text
        }
    ],

    "temperature": 0.0,  
    "top_p": 1.0,        
    "max_tokens": len(input_text.split()) + 10, 
    "stop": None,        
    "n": 1,              
    "logit_bias": {
        "<extra_token>": -100 
    }

}


    try:
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response generated.")
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    input_text = "d o n"
    output = generate_sentences(input_text)
    
    print("Input Text:", input_text)
    print("Generated Sentences:", output)

