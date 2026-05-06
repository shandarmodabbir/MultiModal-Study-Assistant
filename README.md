# MultiModal Study Assistant

A local AI-powered study tool that takes **text, PDFs, and audio** and turns them into structured learning material like notes, flashcards, and MCQs.

The goal of this project is to make studying more efficient by automatically converting raw content into active learning formats.

---

## Features

- Accepts multiple input formats:
  - Text
  - PDF documents
  - Audio (work in progress)

- Generates:
  - Concise notes
  - Flashcards for revision
  - Multiple-choice questions (MCQs)

- Uses Gemini API (LLM) for content understanding and generation

---

## Tech Stack

- Python
- Gemini API (LLM for content generation)
- PDF processing libraries
- Basic audio processing (currently unstable)

---

## Current Limitations

- Audio pipeline is not fully stable  
  (initial attempts using Google SR resulted in errors)

- Performance depends on input quality (especially PDFs and audio)

---

## Future Improvements

- Integrate Whisper for better audio transcription
- Improve MCQ quality and difficulty levels
- Support more file formats (videos, images)

---

## Setup

```bash
git clone https://github.com/shandarmodabbir/MultiModal-Study-Assistant.git
cd MultiModal-Study-Assistant
pip install -r requirements.txt
