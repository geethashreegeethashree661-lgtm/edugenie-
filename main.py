import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google import genai

app = FastAPI(title="EduGenie Learning Assistant")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": "",
            "question": ""
        }
    )


@app.post("/ask")
async def ask_question(
    request: Request,
    question: str = Form(...),
    task: str = Form(...)
):
    if not client:
        result = "Gemini API key is not configured. Add GEMINI_API_KEY in Render Environment Variables."
    else:
        prompts = {
            "qa": "Answer this question clearly for a student:",
            "explain": "Explain this topic in simple words:",
            "summary": "Summarize the following text into key points:",
            "quiz": "Create 3 multiple-choice questions from this text. Give 4 options for each and identify the correct answer.",
            "learn": "Create a step-by-step learning path from beginner to advanced level for this topic."
        }
        prompt = prompts.get(task, prompts["qa"])
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{prompt}\n\n{question}"
            )
            result = response.text or "No response generated."
        except Exception:
            result = "Unable to generate a response. Check your Gemini API key, API access, and try again."

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": result, "question": question}
    )


@app.get("/health")
async def health():
    return {"status": "ok", "application": "EduGenie"}
