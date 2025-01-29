import unittest
import os
import json
from datetime import datetime
from utils import (
    validate_api_key,
    save_response_to_json,
    extract_first_page_as_image,
    read_prompt_template
)

class TestPDFAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_responses_dir = "responses"
        self.test_response_file = os.path.join(self.test_responses_dir, "responses.json")
        
        # Ensure test directory exists
        os.makedirs(self.test_responses_dir, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test response file if it exists
        if os.path.exists(self.test_response_file):
            with open(self.test_response_file, 'w') as f:
                json.dump([], f)

    def test_api_key_validation(self):
        """Test API key validation."""
        self.assertTrue(validate_api_key("valid_key_12345"))
        self.assertFalse(validate_api_key(""))
        self.assertFalse(validate_api_key("   "))

    def test_save_response(self):
        """Test saving analysis response to JSON."""
        test_pdf = "test.pdf"
        test_result = "Test analysis result"
        
        # Save a test response
        save_response_to_json(test_pdf, test_result)
        
        # Verify the response was saved correctly
        self.assertTrue(os.path.exists(self.test_response_file))
        
        with open(self.test_response_file, 'r') as f:
            responses = json.load(f)
            
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]["pdf_name"], test_pdf)
        self.assertEqual(responses[0]["analysis_result"], test_result)
        self.assertTrue("timestamp" in responses[0])

    def test_prompt_template(self):
        """Test reading prompt template."""
        prompt = read_prompt_template()
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_extract_first_page_invalid_pdf(self):
        """Test extraction with invalid PDF."""
        invalid_pdf_bytes = b"Not a PDF file"
        result = extract_first_page_as_image(invalid_pdf_bytes)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
