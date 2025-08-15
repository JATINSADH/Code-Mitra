# gemini_client.py
# This module handles all communication with the Google Gemini API.

import requests
import time

# --- Configuration ---
# IMPORTANT: Replace with your actual Gemini API key.
API_KEY = "AIzaSyCKEHZlvP1L1epBt1Hqz5nvynL44PkNdnk"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def query_gemini(prompt: str) -> str:
    """
    Sends a prompt to the Gemini API with exponential backoff for rate limiting.
    """
    if not API_KEY or API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Error: Gemini API key is not set in `gemini_client.py`."

    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    retries = 3
    delay = 1
    for i in range(retries):
        try:
            # Set a 30-second timeout for the request
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 429:
                raise requests.exceptions.HTTPError(f"429 Too Many Requests", response=response)

            response.raise_for_status()
            
            response_json = response.json()
            if 'candidates' in response_json and response_json['candidates']:
                return response_json['candidates'][0]['content']['parts'][0]['text']
            else:
                return "AI model returned no content. This might be due to safety filters."
        
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                if i < retries - 1:
                    print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    return "API Error: The server is still busy after multiple retries. Please wait a moment."
            else:
                return f"API Request Error: {e}"
        except requests.exceptions.Timeout:
            return "API Request Error: The request timed out. Please check your internet connection."
        except requests.exceptions.RequestException as e:
            return f"API Request Error: {e}"
        except (KeyError, IndexError) as e:
            return f"Error parsing API response: {e}\n\nRaw Response:\n{response.text}"
    
    return "API Error: The server is busy. Please try again later."
