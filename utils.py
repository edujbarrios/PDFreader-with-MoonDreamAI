import base64
import io
from typing import Tuple, Optional
import fitz  # PyMuPDF
from PIL import Image
from openai import OpenAI
import os

def read_prompt_template() -> str:
    """Read the prompt template from prompts/prompt.md"""
    try:
        with open("prompts/prompt.md", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback prompt in case the file is not found
        return """Please analyze this PDF cover page and provide a detailed analysis with Title, Authors, Institution, Date, Visual Elements, Document Type, and Identifiers."""

def validate_api_key(api_key: str) -> bool:
    """Validate the Moondream API key format."""
    return len(api_key.strip()) > 0

def extract_first_page_as_image(pdf_bytes: bytes) -> Optional[bytes]:
    """Extract the first page of a PDF and convert it to an image."""
    try:
        # Open PDF from memory
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        if len(pdf_document) == 0:
            return None

        # Get first page
        first_page = pdf_document[0]

        # Convert to image with higher resolution
        pix = first_page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_document.close()
        return img_byte_arr
    except Exception as e:
        print(f"Error extracting PDF page: {e}")
        return None

def analyze_image_with_moondream(api_key: str, image_bytes: bytes) -> Tuple[bool, str]:
    """Analyze image using Moondream API."""
    try:
        client = OpenAI(
            base_url="https://api.moondream.ai/v1",
            api_key=api_key
        )

        # Convert image to base64
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Get prompt from file
        prompt = read_prompt_template()

        # Create the API request
        response = client.chat.completions.create(
            model="moondream-2B",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        return True, response.choices[0].message.content
    except Exception as e:
        return False, f"Error analyzing image: {str(e)}"