"""
utils/audio.py
--------------
Convert audio files to text.

Two engines:
  1. Google Speech Recognition (free, no key, lower accuracy)
  2. OpenAI Whisper API       (paid, needs key, much better for lectures)

Supported formats: .wav .mp3 .m4a .ogg .flac
Requires: ffmpeg (already installed)

Usage:
    from utils.audio import transcribe_audio

    # Google SR (default)
    text = transcribe_audio("lecture.mp3")

    # Whisper
    text = transcribe_audio("lecture.mp3", engine="whisper")
"""

import os
import math
import tempfile
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment


# ── Config ───────────────────────────────────────────────────
CHUNK_SECONDS = 55   # Google SR works best with chunks under 60s


# ─────────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────

def _convert_to_wav(file_path: str, tmp_dir: str) -> str:
    """
    Convert any supported audio format to mono 16kHz WAV.
    This is what Google SR and Whisper both work best with.

    Why mono?    SR models expect single-channel audio.
    Why 16kHz?   Standard for speech recognition — higher is wasteful.
    """
    path   = Path(file_path)
    suffix = path.suffix.lower()
    fmt_map = {
        ".mp3":  "mp3",
        ".m4a":  "m4a",
        ".ogg":  "ogg",
        ".flac": "flac",
        ".wav":  "wav",
    }
    fmt = fmt_map.get(suffix)
    if fmt is None:
        raise ValueError(
            f"Unsupported audio format: '{suffix}'\n"
            f"Supported: {list(fmt_map.keys())}"
        )

    print(f"  Converting {path.name} → WAV (mono, 16kHz)...")
    audio = AudioSegment.from_file(str(path), format=fmt)
    audio = audio.set_channels(1).set_frame_rate(16000)

    wav_path = os.path.join(tmp_dir, "converted.wav")
    audio.export(wav_path, format="wav")
    return wav_path


def _split_wav(wav_path: str, chunk_seconds: int, tmp_dir: str) -> list[str]:
    """
    Split a WAV file into fixed-length chunks.

    Why split?
    Google SR has a ~60 second limit per request.
    Splitting lets us handle lectures of any length.
    """
    audio       = AudioSegment.from_wav(wav_path)
    duration_ms = len(audio)
    chunk_ms    = chunk_seconds * 1000
    n_chunks    = math.ceil(duration_ms / chunk_ms)

    duration_mins = duration_ms / 60000
    print(f"  Audio duration : {duration_mins:.1f} minutes")
    print(f"  Splitting into : {n_chunks} chunk(s) of {chunk_seconds}s each")

    chunk_paths = []
    for i in range(n_chunks):
        chunk      = audio[i * chunk_ms : (i + 1) * chunk_ms]
        chunk_path = os.path.join(tmp_dir, f"chunk_{i:04d}.wav")
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)

    return chunk_paths


def _transcribe_chunk_google(wav_path: str, recognizer: sr.Recognizer) -> str:
    """
    Transcribe one WAV chunk using Google Speech Recognition.
    Free — no API key needed. Uses Google's public SR endpoint.
    """
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""   # chunk was inaudible — skip silently
    except sr.RequestError as e:
        raise RuntimeError(f"Google SR API error: {e}") from e


def _transcribe_whisper(file_path: str) -> str:
    """
    Transcribe using OpenAI Whisper API.

    Much better accuracy for:
    - Lectures with technical terms
    - Accented speech
    - Background noise

    Requires:
        pip install openai
        OPENAI_API_KEY set in .env
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package not installed.\n"
            "Run: pip install openai"
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set.\n"
            "Add to your .env file:\n"
            "OPENAI_API_KEY=sk-..."
        )

    client = OpenAI(api_key=api_key)
    print("  Sending to Whisper API...")

    with open(file_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
        )
    return result


# ─────────────────────────────────────────────────────────────
# PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────

def transcribe_audio(
    file_path:   str,
    engine:      str = "google",
    progress_cb: callable = None,
) -> str:
    """
    Transcribe an audio file to text.

    Args:
        file_path:   Path to the audio file (.wav .mp3 .m4a .ogg .flac)
        engine:      "google" (free) or "whisper" (better accuracy, needs key)
        progress_cb: Optional callable(current_chunk, total_chunks)
                     Used by Streamlit to show a progress bar.

    Returns:
        Full transcript as a single string.

    Raises:
        FileNotFoundError : file doesn't exist
        ValueError        : unsupported format
        RuntimeError      : transcription failed
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    if engine not in ("google", "whisper"):
        raise ValueError(f"Unknown engine: '{engine}'. Use 'google' or 'whisper'.")

    print(f"\n🎙️ Transcribing: {path.name}")
    print(f"   Engine: {engine}")

    with tempfile.TemporaryDirectory() as tmp_dir:

        # ── Step 1: convert to WAV ────────────────────────────
        wav_path = _convert_to_wav(str(path), tmp_dir)

        # ── Step 2: transcribe ────────────────────────────────
        if engine == "whisper":
            # Whisper handles the whole file at once — no chunking needed
            transcript = _transcribe_whisper(wav_path)

        else:
            # Google SR needs chunking
            chunks     = _split_wav(wav_path, CHUNK_SECONDS, tmp_dir)
            total      = len(chunks)
            recognizer = sr.Recognizer()

            transcript_parts = []
            for i, chunk_path in enumerate(chunks, 1):
                print(f"  Chunk {i}/{total}...")
                if progress_cb:
                    progress_cb(i, total)
                part = _transcribe_chunk_google(chunk_path, recognizer)
                if part:
                    transcript_parts.append(part)

            transcript = " ".join(transcript_parts)

    # ── Step 3: validate ──────────────────────────────────────
    if not transcript.strip():
        raise RuntimeError(
            "Transcription returned empty text.\n"
            "Tips:\n"
            "  - Check audio quality (no loud background noise)\n"
            "  - Try a different engine (whisper is more accurate)\n"
            "  - Make sure the audio has clear speech"
        )

    print(f"  ✅ Transcript: {len(transcript):,} characters")
    return transcript