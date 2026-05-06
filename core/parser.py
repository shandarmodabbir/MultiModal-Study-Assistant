"""
core/parser.py
--------------
Orchestrates the 3 LLM functions and assembles the final result.
Also saves and loads results as JSON files.
"""

import json
from pathlib import Path
from datetime import datetime
from core.llm import generate_notes, generate_flashcards, generate_mcqs


def process_text(text: str) -> dict:
    print("📝 Generating notes...")
    notes = generate_notes(text)

    print("🃏 Generating flashcards...")
    flashcards = generate_flashcards(text)

    print("❓ Generating MCQs...")
    mcqs = generate_mcqs(text)

    print("✅ Done!")
    return {
        "notes":      notes,
        "flashcards": flashcards,
        "mcqs":       mcqs,
    }


def save_to_json(data: dict, output_dir: str = "outputs") -> str:
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"lecture_output_{timestamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to {path}")
    return str(path)


def load_from_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)