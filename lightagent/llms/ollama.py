from llms.base_LLM import BaseLLM
import requests

class Ollama(BaseLLM):
    def __init__(self, model_name="llama3.1"):
        self.model_name = model_name
        self.ollama_base = "http://localhost:11434"

    def __init__(self, model_name="llama3.1", ollama_base="http://localhost:11434"):
        self.model_name = model_name
        self.ollama_base = ollama_base

    def generate(self, input, reasoning=True):
        url = f"{self.ollama_base}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": input,
            "stream": False
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response']