from typing import Dict, List

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError


app = FastAPI(title="AI Mystery")

templates = Jinja2Templates(directory="templates")

LLM_URL = "http://127.0.0.1:8001/v1/chat/completions"


SUSPECTS = {
    "alex": {
        "name": "Alex",
        "role": "Backend Developer",
        "facts": [
            "Alex left the office at 18:20.",
            "Alex had access to the prototype room.",
            "Alex spoke with Maya before leaving.",
        ],
    },
    "maya": {
        "name": "Maya",
        "role": "Product Designer",
        "facts": [
            "Maya stayed in the design room until 18:40.",
            "Maya did not have a prototype room key.",
            "Maya saw Daniel near the prototype room.",
        ],
    },
    "daniel": {
        "name": "Daniel",
        "role": "Lab Manager",
        "facts": [
            "Daniel had a prototype room key.",
            "Daniel was near the prototype room at 18:30.",
            "Daniel knew where the prototype was stored.",
        ],
    },
}

CULPRIT = "daniel"


class AskRequest(BaseModel):
    suspect: str
    question: str
    history: List[Dict[str, str]] = []


class LLMResponse(BaseModel):
    reply: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "suspects": SUSPECTS,
        },
    )


def build_prompt(suspect: dict, question: str, history: list) -> str:
    facts = "\n".join(f"- {fact}" for fact in suspect["facts"])

    previous = "\n".join(
        f'{item["role"]}: {item["content"]}'
        for item in history[-6:]
    )

    return f"""
You are role-playing as {suspect["name"]}, a {suspect["role"]}.

You are a suspect in a workplace mystery.

IMPORTANT RULES:
- Only use the facts provided below.
- Do not invent events, people, locations or times.
- Stay in character.
- Do not directly confess.
- Answer the investigator's question naturally.
- Return ONLY valid JSON.

Your hidden facts:
{facts}

Previous conversation:
{previous}

Investigator question:
{question}

Return exactly:
{{"reply": "your answer"}}
""".strip()


async def ask_llm(prompt: str) -> LLMResponse:
    payload = {
        "model": "local",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.4,
        "response_format": {
            "type": "json_object"
        },
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(LLM_URL, json=payload)
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"].strip()

    if content.startswith("```"):
        lines = content.splitlines()
        lines = [line for line in lines if not line.strip().startswith("```")]
        content = "\n".join(lines).strip()

    return LLMResponse.model_validate_json(content)


@app.post("/api/ask")
async def ask(request: AskRequest):
    suspect = SUSPECTS.get(request.suspect.lower())

    if not suspect:
        return {"error": "Unknown suspect"}

    if not request.question.strip():
        return {"error": "Question cannot be empty"}

    prompt = build_prompt(
        suspect,
        request.question,
        request.history,
    )

    try:
        result = await ask_llm(prompt)
    except (ValidationError, KeyError, ValueError):
        return {"error": "The model returned an invalid response."}
    except httpx.HTTPError as exc:
        return {"error": f"LLM connection failed: {exc}"}

    return {
        "suspect": suspect["name"],
        "reply": result.reply,
    }


@app.post("/api/accuse/{suspect}")
async def accuse(suspect: str):
    suspect = suspect.lower()

    if suspect not in SUSPECTS:
        return {"error": "Unknown suspect"}

    correct = suspect == CULPRIT

    return {
        "correct": correct,
        "message": (
            "You solved the mystery."
            if correct
            else "Wrong suspect. The mystery remains unsolved."
        ),
    }
