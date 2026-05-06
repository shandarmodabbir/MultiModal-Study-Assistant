"""
core/llm.py
-----------
All LLM interactions via Google Gemini.

Three public functions:
  - generate_notes(text)      → list of bullet-point strings
  - generate_flashcards(text) → list of {"q": ..., "a": ...} dicts
  - generate_mcqs(text)       → list of {"question", "options", "answer", "difficulty"} dicts
"""

import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads .env file into os.environ


# ─────────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────

def _call(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "\nGEMINI_API_KEY not set!\n"
            "Add this to your .env file:\n"
            "GEMINI_API_KEY=your-key-here\n"
        )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
    )
    return response.text.strip()


def _extract_json(raw: str) -> dict | list:
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    # fix trailing commas before ] or } — illegal in JSON but Gemini sometimes adds them
    cleaned = re.sub(r",\s*(\]|\})", r"\1", cleaned)



    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Could not parse Gemini output as JSON.\n"
            f"Error: {e}\n"
            f"Raw output:\n{raw}"
        ) from e


# ─────────────────────────────────────────────────────────────
# PUBLIC FUNCTIONS
# ─────────────────────────────────────────────────────────────

def generate_notes(text: str) -> list[str]:
    prompt = f"""
You are an expert academic tutor. Read the following lecture content and produce
clear, concise revision notes.

RULES:
- Return ONLY a JSON array of strings. No markdown, no extra keys, nothing else.
- Each string = one bullet point (1-2 sentences max).
- Cover all key concepts, definitions, formulas, and examples.
- Aim for 10-20 points depending on content length.

LECTURE CONTENT:
\"\"\"{text[:12000]}\"\"\"

OUTPUT FORMAT:
["First point here.", "Second point here.", "..."]
"""
    raw = _call(prompt)
    result = _extract_json(raw)
    if not isinstance(result, list):
        raise ValueError("Expected a JSON array for notes.")
    return [str(item) for item in result]


def generate_flashcards(text: str) -> list[dict]:
    prompt = f"""
You are an expert academic tutor creating study flashcards.

RULES:
- Return ONLY a JSON array of objects. No markdown, nothing else.
- Each object must have exactly two keys: "q" (question) and "a" (answer).
- Create 10-15 flashcards covering important terms, concepts, and facts.
- Questions must be specific and testable.
- Answers must be concise (1-3 sentences).

LECTURE CONTENT:
\"\"\"{text[:12000]}\"\"\"

OUTPUT FORMAT:
[
  {{"q": "What is X?", "a": "X is defined as ..."}},
  {{"q": "What formula describes Y?", "a": "Y = ..."}}
]
"""
    raw = _call(prompt)
    result = _extract_json(raw)
    if not isinstance(result, list):
        raise ValueError("Expected a JSON array for flashcards.")
    valid = []
    for item in result:
        if isinstance(item, dict) and "q" in item and "a" in item:
            valid.append({"q": str(item["q"]), "a": str(item["a"])})
    return valid


def generate_mcqs(text: str) -> list[dict]:
    prompt = f"""
You are an expert exam-paper writer. Generate exactly 10 multiple-choice questions.

RULES:
- Return ONLY a JSON array of exactly 10 objects. No markdown, nothing else.
- Each object must have these exact keys:
    "question"   : the question text (string)
    "options"    : list of exactly 4 strings starting with "A) ", "B) ", "C) ", "D) "
    "answer"     : one capital letter — "A", "B", "C", or "D"
    "difficulty" : one of "Easy", "Medium", or "Hard"
- Mix: roughly 3 Easy, 4 Medium, 3 Hard.
- Test understanding, not memorisation.
- All 4 options must be plausible.

LECTURE CONTENT:
\"\"\"{text[:12000]}\"\"\"

OUTPUT FORMAT:
[
  {{
    "question": "Which of the following best describes X?",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "answer": "B",
    "difficulty": "Medium"
  }}
]
"""
    raw = _call(prompt)
    result = _extract_json(raw)
    if not isinstance(result, list):
        raise ValueError("Expected a JSON array for MCQs.")
    valid = []
    for item in result:
        if (
            isinstance(item, dict)
            and "question"   in item
            and "options"    in item
            and "answer"     in item
            and "difficulty" in item
            and len(item["options"]) == 4
        ):
            valid.append({
                "question":   str(item["question"]),
                "options":    [str(o) for o in item["options"]],
                "answer":     str(item["answer"]).upper(),
                "difficulty": str(item["difficulty"]),
            })
    return valid[:10]