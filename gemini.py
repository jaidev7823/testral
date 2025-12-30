# gemini.py
from google import genai
from google.genai import types
import base64, os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def explain_failure(image_path, test_name):
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": f"This e-commerce test failed: {test_name}. Explain the visible issue briefly for a founder."},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": img
                        }
                    }
                ]
            }
        ]
    )

    return response.text
