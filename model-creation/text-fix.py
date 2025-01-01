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
                    "You are an AI assistant. Correct and organize the following "
                    "input into proper sentences with correct grammar and spacing."
                    "Do not translate it into any other language or do any other operation than correcting the text."
                    "Do not put the text in bold or something else."
                    "Do not write anything else except the corrected text."
                )
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
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
    input_text = "helohowareyoutodayIhopethisworks"
    
    # Generate proper sentences
    output = generate_sentences(input_text)
    
    print("Input Text:", input_text)
    print("Generated Sentences:", output)

