import os
from dotenv import load_dotenv
load_dotenv()  # loads .env

from google import genai
from google.genai import types
from dateutil import parser as dateparser

client = genai.Client(
    vertexai=True,
    api_key=os.getenv("GOOGLE_CLOUD_API_KEY")  # optional if using API key
)

model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro-002")
resp = client.models.generate_content(
    model=model_name,
    contents=contents,
    config=config,
)
