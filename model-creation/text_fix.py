import requests
import os
from dotenv import load_dotenv 

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise ValueError("API key not found in .env file. Please add PERPLEXITY_API_KEY to your .env file.")

BASE_URL = "https://api.perplexity.ai"

# Function to process unorganized words and generate proper sentences
def generate_sentences(input_text):
    """
    Uses the Perplexity API to convert unorganized words into proper sentences.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Define the payload for the API request
    payload = {
    "model": "llama-3.1-sonar-small-128k-online",  # Cost-effective model
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

    "temperature": 0.0,  # Ensures deterministic output for correction tasks
    "top_p": 1.0,        # Ensures all probability mass is considered for deterministic behavior
    "max_tokens": len(input_text.split()) + 10,  # Allows sufficient tokens for corrected output
    "stop": None,        # Ensures the model doesn't stop prematurely
    "n": 1,              # Returns only one response
    "logit_bias": {      # Penalizes the model from generating extra explanations or outputs
        "<extra_token>": -100  # Replace <extra_token> with tokens corresponding to unwanted output
    }

}


    try:
        # Make the API request
        response = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Extract and return the generated response
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response generated.")
    
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    # Input: Unorganized words with errors and no spaces
    input_text = "d o n"
    
    # Generate proper sentences
    output = generate_sentences(input_text)
    
    print("Input Text:", input_text)
    print("Generated Sentences:", output)

