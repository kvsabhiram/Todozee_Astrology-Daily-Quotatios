# 
"""
llm_client.py
-------------
Direct Gemma 4 E2B-IT loading using Transformers.
No Ollama required.

Install:
    pip install torch transformers accelerate sentencepiece
"""

import os
import json
import time
from datetime import datetime

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

# =========================================================
# MODEL CONFIG
# =========================================================

MODEL_NAME = "google/gemma-4-E2B-it"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =========================================================
# LOGGING
# =========================================================
# Every model call (input prompt + generated output) is appended
# as one JSON line to logs/gemma_io.jsonl for later inspection.

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "gemma_io.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


def _log_io(prompt: str, response: str, **meta) -> None:
    """Append one input/output record to the log file."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "input": prompt,
        "output": response,
        **meta,
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[llm_client] failed to write log: {e}")

# =========================================================
# LOAD PROCESSOR + MODEL
# =========================================================

print("Loading processor...")
processor = AutoProcessor.from_pretrained(MODEL_NAME)

print("Loading model...")
if DEVICE == "cuda":
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_NAME,
        dtype=torch.bfloat16,
        device_map="auto",
    )
else:
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_NAME,
        dtype=torch.float32,
    ).to(DEVICE)

model.eval()

print(f"Model loaded on: {DEVICE}")

# =========================================================
# GENERATION FUNCTION
# =========================================================

def call_gemma(
    prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.7,
) -> str:
    """
    Generate text from Gemma 4 E2B-IT
    """

    # Proper chat formatting for instruction model
    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]

    start = time.time()

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
            pad_token_id=processor.tokenizer.eos_token_id,
        )

    elapsed = time.time() - start

    # Only decode newly generated tokens
    generated_tokens = outputs[0][input_len:]

    response = processor.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    cleaned = clean_output(response)

    _log_io(
        prompt,
        cleaned,
        max_tokens=max_tokens,
        temperature=temperature,
        input_tokens=int(input_len),
        output_tokens=int(generated_tokens.shape[-1]),
        seconds=round(elapsed, 2),
    )

    return cleaned


# =========================================================
# CLEAN OUTPUT
# =========================================================

def clean_output(text: str) -> str:

    if not text:
        return ""

    text = text.strip()

    prefixes = [
        "Here is your",
        "Here's your",
        "Here is the",
        "Here's the",
        "Sure!",
        "Of course!",
        "Certainly!",
        "Okay,",
    ]

    for p in prefixes:

        if text.lower().startswith(p.lower()):

            if "\n" in text:
                text = text.split("\n", 1)[1].strip()
            else:
                text = text[len(p):].strip()

    # Remove wrapping quotes
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1].strip()

    return text


# =========================================================
# STATUS CHECK
# =========================================================

def check_model_status():

    return {
        "model_loaded": model is not None,
        "model_name": MODEL_NAME,
        "device": str(model.device),
        "cuda_available": torch.cuda.is_available(),
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    prompt = "Explain transformers in simple words."

    response = call_gemma(prompt)

    print("\n=== RESPONSE ===\n")
    print(response)