# Code-Mitra - An Intelligent Python Assistant & Editor
Code-Mitra is a desktop application built entirely in Python that serves as a real-time AI coding assistant. It integrates the power of Google's Gemini API to provide intelligent code explanations, error solutions, and code generation, helping to boost developer productivity.

## Key Features
Live Code Editor: An interactive editor to write, run, and save Python code.
AI-Powered Analysis: Get instant explanations, alternative approaches, and optimization tips for your code.
Error Solutions: Automatically detects errors using pylint and provides AI-generated solutions.
Dual-Mode "Ask AI":
Code Generation: Ask the AI to generate new code snippets.
Contextual Q&A: Ask questions about the code currently in the editor.
File Monitoring: Automatically analyzes files when they are saved in a selected project folder.

## Technology Stack
Language: Python 3
GUI: Tkinter (with ttk themed widgets)
AI Integration: Google Gemini API
Libraries: requests, watchdog, pylint

## How to Run
Clone the repository:
git clone https://github.com/your-username/Code-Mitra.git
cd Code-Mitra
Install dependencies:
pip install -r requirements.txt
Add your API Key:
Open the gemini_client.py file.
Replace "YOUR_GEMINI_API_KEY_HERE" with your actual Google Gemini API key.
Run the application:
python main_app.py

# Improtant for gemini api creation
### API Key Configuration
This project requires a Google Gemini API key to function.
Go to Google AI Studio.
Sign in with your Google account.
Click on the "Get API key" button.
Click "Create API key in new project" to generate a new key.
Copy the newly generated API key.
Open the gemini_client.py file in the project and paste your key into the following line:
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
Save the file.

**Important: Never share your API key or commit it to a public GitHub repository.**
