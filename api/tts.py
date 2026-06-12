# api/tts.py

import os
import re
import uuid
import tempfile
from typing import List, Optional, Tuple, cast
from time import monotonic
from io import BytesIO
import asyncio
import logging

import httpx
from pydub import AudioSegment
from pydub.utils import which
import PyPDF2
from dotenv import load_dotenv
from pathlib import Path
from elevenlabs.client import ElevenLabs

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("tts")

# ==== CONFIG ====
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "")
VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # replace with yours
MODEL_ID = os.environ.get("ELEVEN_MODEL_ID", "eleven_multilingual_v2")  # replace if needed
MAX_CHARS = int(os.environ.get("TTS_MAX_CHARS", "2000"))  # bigger than 250 -> fewer calls
CONCURRENCY = int(os.environ.get("TTS_CONCURRENCY", "4"))  # tune based on CPU/network

# === ffmpeg for pydub ===
ffmpeg_path = which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"
ffprobe_path = which("ffprobe") or r"C:\ffmpeg\bin\ffprobe.exe"
os.environ["FFMPEG_BINARY"] = ffmpeg_path
os.environ["FFPROBE_BINARY"] = ffprobe_path

BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

client = ElevenLabs(api_key=ELEVEN_API_KEY)

# ==== TEXT UTILITIES (all O(n)) ====
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def cleanup_text(raw: str) -> str:
    if not raw:
        return ""
    txt = re.sub(r"-\s*\n\s*", "", raw)   # join hyphenated line breaks
    txt = re.sub(r"\s*\n\s*", " ", txt)   # newlines -> space
    txt = re.sub(r"\s{2,}", " ", txt)     # collapse whitespace
    return txt.strip()


def sentences(text: str) -> List[str]:
    text = cleanup_text(text)
    if not text:
        return []
    sents = _SENTENCE_SPLIT.split(text)
    return [s.strip() for s in sents if s.strip()]


def pack_sentences(sents: List[str], limit: int) -> List[str]:
    """Greedy pack sentences into chunks <= limit chars (linear time)."""
    chunks: List[str] = []
    cur = ""
    for s in sents:
        if not cur:
            cur = s
        elif len(cur) + 1 + len(s) <= limit:
            cur += " " + s
        else:
            chunks.append(cur)
            cur = s
        # If a single sentence is longer than limit, fall back to word-wrap split
        if len(cur) > limit:
            words = cur.split()
            cur = ""
            for w in words:
                if not cur:
                    cur = w
                elif len(cur) + 1 + len(w) <= limit:
                    cur += " " + w
                else:
                    chunks.append(cur)
                    cur = w
    if cur:
        chunks.append(cur)
    return chunks


def chunk_text_for_tts(text: str, limit: int = MAX_CHARS) -> List[str]:
    sents = sentences(text)
    if not sents:
        return []
    # If there’s no punctuation, pack_sentences still handles long runs via word-wrap fallback
    return pack_sentences(sents, limit)


# ==== ELEVENLABS TTS (async + concurrent) ====
ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
HEADERS = {
    "xi-api-key": ELEVEN_API_KEY,
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
}


async def tts_request(text: str) -> bytes:
    """
    Single TTS call to ElevenLabs; returns MP3 bytes.
    Uses the official ElevenLabs Python client under the hood.
    """
    if not ELEVEN_API_KEY:
        raise RuntimeError("Missing ELEVEN_API_KEY")

    def _call() -> bytes:
        # Raw response so we can access headers if needed
        # NOTE: pass voice settings via the SDK model if needed; omit untyped dict to satisfy the
        # typed client signature (VoiceSettings | None).
        with client.text_to_speech.with_raw_response.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
        ) as response:
            # Example: character usage if you want to log/monitor:
            char_cost = response.headers.get("x-character-count")
            logger.debug("ElevenLabs char cost: %s", char_cost)
            data = response.data
            # If the SDK returns raw bytes, just return them; if it returns an iterator of byte chunks,
            # join them into a single bytes object so the function signature is respected.
            if isinstance(data, (bytes, bytearray)):
                return bytes(data)
            try:
                return b"".join(data)
            except TypeError:
                # Fallback: iterate and accumulate into a BytesIO buffer
                buf = BytesIO()
                for chunk in data:
                    buf.write(chunk)
                return buf.getvalue()

    # Run the blocking ElevenLabs client call in a thread to keep async API
    return await asyncio.to_thread(_call)

# from elevenlabs.client import ElevenLabs
# client = ElevenLabs(api_key="your_api_key")
# # Get raw response with headers
# response = client.text_to_speech.with_raw_response.convert(
#     text="Hello, world!",
#     voice_id="voice_id"
# )
# # Access character cost from headers
# char_cost = response.headers.get("x-character-count")
# audio_data = response.data
    


async def text_to_audio_eleven(text: str, out_path: Optional[str] = None) -> str:
    """
    Chunk text (smart), TTS concurrently, concat once, write MP3.
    Returns the output file path.
    """
    chunks = chunk_text_for_tts(text, limit=MAX_CHARS)
    logger.info("eleven: chunks=%d limit=%d concurrency=%d", len(chunks), MAX_CHARS, CONCURRENCY)
    if not chunks:
        raise ValueError("No speakable content after cleanup/splitting.")
    print(f"ElevenLabs: {len(chunks)} chunk(s), limit={MAX_CHARS}, concurrency={CONCURRENCY}")

    sem = asyncio.Semaphore(CONCURRENCY)

    async def _task(i: int, t: str):
        async with sem:
            try:
                audio = await tts_request(t)  # <-- no client arg now
                logger.debug("eleven: chunk%d ok bytes=%d", i, len(audio))
                return i, audio
            except Exception as e:
                logger.error("eleven: chunk%d failed %s", i, e)
                raise

    # No httpx client needed anymore
    tasks = [asyncio.create_task(_task(i, t)) for i, t in enumerate(chunks)]
    results = await asyncio.gather(*tasks)

    # restore order by index
    results.sort(key=lambda x: x[0])
    mp3_bytes_list = [b for _, b in results]

    # concat once with pydub – still using BytesIO blobs
    combined = AudioSegment.empty()
    for blob in mp3_bytes_list:
        combined += AudioSegment.from_file(BytesIO(blob), format="mp3")

    if not out_path:
        filename = f"{uuid.uuid4().hex}.mp3"
        out_path = str(AUDIO_DIR / filename)

    combined.export(out_path, format="mp3")
    print(f"Final audio => {out_path}")
    return out_path


# Optional: PDF → Audio utility (if you still want it)
async def pdf_to_audio_file(pdf_bytes: bytes, merge: bool = True) -> dict:
    """
    Take a PDF as bytes, extract text per page, run TTS, return dict with
    'mode' and file URLs (relative paths).
    This is logic-only; you can wrap it in a FastAPI endpoint in main.py.
    """
    t0 = monotonic()
    req_id = uuid.uuid4().hex[:8]
    logger.info("pdf-to-audio[%s]: starting", req_id)

    # Persist upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
        tmp.write(pdf_bytes)

    # Read & extract text
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        pages: List[Tuple[int, str]] = []
        for i, page in enumerate(reader.pages):
            txt = cleanup_text(page.extract_text() or "")
            if txt:
                pages.append((i, txt))
        logger.info("pdf-to-audio[%s]: extracted text pages=%d", req_id, len(pages))
    finally:
        try:
            os.remove(pdf_path)
        except Exception:
            logger.warning("pdf-to-audio[%s]: could not remove temp pdf", req_id)

    if not pages:
        return {"error": "No text could be extracted from the PDF."}

    base_id = uuid.uuid4().hex
    file_paths: List[str] = []
    audio_segments: List[AudioSegment] = []

    async def render_one(idx: int, text: str) -> Tuple[int, str]:
        out_filename = f"{base_id}_page{idx+1}.mp3"
        out_full_path = AUDIO_DIR / out_filename
        ts = monotonic()
        logger.info("pdf-to-audio[%s]: TTS start page=%d", req_id, idx + 1)
        await text_to_audio_eleven(text, str(out_full_path))
        logger.info(
            "pdf-to-audio[%s]: TTS ok page=%d ms=%d out=%s",
            req_id, idx + 1, int((monotonic() - ts) * 1000), out_full_path
        )
        return idx, str(out_full_path)

    t_tts = monotonic()
    tasks = [render_one(i, t) for i, t in pages]
    gathered = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(
        "pdf-to-audio[%s]: TTS total ms=%d",
        req_id, int((monotonic() - t_tts) * 1000)
    )

    ok_results: List[Tuple[int, str]] = []
    failed_count = 0
    for r in gathered:
        if isinstance(r, Exception):
            failed_count += 1
            logger.exception("pdf-to-audio[%s]: TTS page failed", req_id, exc_info=r)
        else:
            ok_results.append(cast(Tuple[int, str], r))

    if not ok_results:
        return {
            "error": "TTS failed for all pages. Check server logs for details."
        }

    ok_results.sort(key=lambda x: x[0])

    for _, out_path in ok_results:
        file_paths.append(out_path)
        try:
            audio_segments.append(AudioSegment.from_file(out_path, format="mp3"))
        except Exception as e:
            logger.exception("pdf-to-audio[%s]: failed to read MP3", req_id)

    if merge and audio_segments:
        t_merge = monotonic()
        merged = audio_segments[0]
        for seg in audio_segments[1:]:
            merged += seg
        merged_name = f"{base_id}_merged.mp3"
        merged_path = AUDIO_DIR / merged_name
        merged.export(merged_path, format="mp3")
        logger.info(
            "pdf-to-audio[%s]: merged parts=%d ms=%d -> %s",
            req_id, len(audio_segments), int((monotonic() - t_merge) * 1000), merged_path
        )
        logger.info(
            "pdf-to-audio[%s]: DONE mode=merged total_ms=%d",
            req_id, int((monotonic() - t0) * 1000)
        )
        return {"mode": "merged", "file": str(merged_path), "parts": file_paths}

    logger.info(
        "pdf-to-audio[%s]: DONE mode=split files=%d total_ms=%d",
        req_id, len(file_paths), int((monotonic() - t0) * 1000)
    )
    return {"mode": "split", "files": file_paths}
