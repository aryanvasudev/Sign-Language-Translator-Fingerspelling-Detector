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
                "You are a specialized AI assistant functioning as a spell checker and auto-corrector. "
                "Your task involves the following steps: "
                "1. If the input contains individual letters separated by spaces, join them into coherent words. "
                "2. Check and correct the spelling of words. "
                "3. Reorganize the corrected words into a meaningful and grammatically correct sentence. "
                "4. Ensure proper punctuation, capitalization, and spacing. "
                "5. Maintain the original intent and meaning of the input text as much as possible. "
                "Guidelines: "
                "1. Always treat the input as potentially containing disjointed letters, spelling errors, or scrambled words. "
                "2. Prioritize clarity and correctness in your corrections. "
                "3. Output only the final corrected text without additional explanations, metadata, or comments. "
                "Examples: "
                "Input: T H I S I S A T E S T S E N T E N C E "
                "Output: This is a test sentence. "
                "Input: THIAS SI A TESST SNETENCE "
                "Output: This is a test sentence. "
                "Input: T H I A S I S A T O E S T S E M N T E N R C E "
                "Output: This is a test sentence. "
                "Input: P R O G R M N G IS F U N "
                "Output: Programming is fun."
            )
        },
        {
            "role": "user",
            "content": input_text
        }
    ],
    "temperature": 0.0,
    "top_p": 1.0,
    "max_tokens": len(input_text.split()) + 15,
    "stop": None,
    "n": 1,
    "logit_bias": {}
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
    input_text = "A L P H O A Z B E T"
    output = generate_sentences(input_text)
    
    print("Input Text:", input_text)
    print("Generated Sentences:", output)
