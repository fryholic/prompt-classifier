import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def classify_prompt(self, prompt: str) -> str:
        # This is a placeholder for the actual classification logic.
        # You would typically send a request to the Gemini API here.
        response = self.model.generate_content(f"Classify the following prompt: {prompt}")
        return response.text
