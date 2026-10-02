# AI Mystery

An AI-powered interrogation game built with FastAPI and a local LLM.

A prototype has disappeared from an office. Three suspects remain.

The player can question suspects using natural language, examine their answers, and eventually accuse one of them.

## Core Idea

The project separates language generation from game logic.

The LLM handles:
- Natural-language dialogue
- Suspect role-play
- Conversation history

The application handles:
- Suspect facts
- Game truth
- Culprit identity
- Accusation logic
- Model output validation

> The LLM handles the conversation. The application handles the truth.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Jinja2
- Vanilla JavaScript
- HTTPX
- llama.cpp
- Qwen2.5-Coder 1.5B

## Running Locally

Start the local model:

    python run_llama.py

Start the application:

    source .venv/bin/activate
    uvicorn app:app --reload

Then open:

    http://127.0.0.1:8000

## Project Structure

    AI-Mystery/
    ├── app.py
    ├── run_llama.py
    ├── requirements.txt
    ├── templates/
    │   └── index.html
    ├── .gitignore
    └── README.md

## Why This Project?

This is intentionally a small project.

The goal is to demonstrate a practical LLM integration rather than build another chatbot.

The project explores a simple architecture:

    LLM = language
    Application = state + rules + truth

Model output is validated before being returned to the client, while game-critical decisions remain deterministic.

## Limitations

The project uses a small 1.5B local model running on CPU.

Because LLM output can occasionally be imperfect, the application does not rely on the model to determine the final game outcome.

The project is intentionally kept small and focused on the core idea.
