import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("Give me an SQL query to get total sales from a table called total_sales")
print(response.text)
