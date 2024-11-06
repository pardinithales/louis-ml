import unittest
import logging
import requests
from src.app import get_llm_response

class TestLouis(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        
    def test_ollama_connection(self):
        """Testa se o Ollama está rodando"""
        try:
            response = requests.get('http://localhost:11434/api/tags')
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.ConnectionError:
            self.fail("Ollama não está rodando em localhost:11434")
            
    def test_llama_response(self):
        """Testa resposta do modelo"""
        prompt = "Liste sintomas: cefaleia"
        response = get_llm_response(prompt)
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()