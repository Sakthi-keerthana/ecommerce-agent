from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import plotly.express as px
import requests  

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    print("✅ Backend is up and running!")

# Gemini LLM Prompt to SQL
def translate_question_to_sql(question: str) -> str:
    prompt = f"""
You are an expert data analyst assistant that converts natural language questions into SQL queries for data visualization.

Database schema:
- ad_sales(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
- total_sales(date, item_id, total_sales, total_units_ordered)
- eligibility(eligibility_datetime_utc, item_id, eligibility, message)

Instructions:
- first identify this can be suitable for visualization. if yes visualize=True, else visualize=False.
- Generate **clean SQL** suitable for plotting charts.
- Ensure the query returns 2-3 columns only for X and Y axis plotting.
- Prefer columns like date, item_id, total_sales, ad_sales, ad_spend, clicks.
- Group and order results appropriately for trend analysis.
- Do NOT include explanations.
- Return only the raw SQL query.

Natural Language Question:
"{question}"
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyDBfdZiDhLkZm8rx8Sxi_cJwtXKeVNazeM"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    try:
        sql = data["candidates"][0]["content"]["parts"][0]["text"]
        return sql.strip("```sql").strip("```").strip()
    except Exception as e:
        return f"-- Error extracting SQL: {e}"




# Endpoint to handle user questions
@app.post("/ask")
async def ask_question(request: Request):
    body = await request.json()
    question = body.get("question")

    try:
        sql_query = translate_question_to_sql(question)

        conn = sqlite3.connect("../db/ecommerce.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        if not result:
            return {
                "question": question,
                "answer": "No data found for your query.",
                "sql_query": sql_query,
                "visualize": False
            }

        if len(columns) == 2 and all(isinstance(row[1], (int, float)) for row in rows):
            x_data = [row[0] for row in rows]
            y_data = [row[1] for row in rows]
            return {
                "question": question,
                "answer": "Here is the visual representation.",
                "sql_query": sql_query,
                "visualize": True,
                "graphType": "bar",
                "graphData": {
                    "x": x_data,
                    "y": y_data,
                    "xLabel": columns[0],
                    "yLabel": columns[1],
                    "title": question.capitalize()
                }
            }

        answer_lines = []
        for row in result:
            line = ', '.join(f"{key}: {value}" for key, value in row.items())
            answer_lines.append(line)
        answer = "\n".join(answer_lines)

        return {
            "question": question,
            "answer": answer,
            "sql_query": sql_query,
            "visualize": False
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing question: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    

    finally:
        if 'conn' in locals():
            conn.close()

