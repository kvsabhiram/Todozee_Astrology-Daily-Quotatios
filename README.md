# Astrology Daily Quotes Backend

FastAPI backend that produces personalized astrology reports and daily
motivational quotes. Calculations use the **Swiss Ephemeris**; text
generation uses **Gemma 4 E2B-IT** loaded directly on the local GPU
via Transformers — no Ollama, no external API calls.

## Project structure

```
Astro_Daily_quatation/
├── README.md
├── requirements.txt
├── .gitignore
├── logs/                       # auto-created at runtime
│   ├── app.jsonl               # one JSON line per API call (input + output)
│   └── gemma_io.jsonl          # one JSON line per model call (prompt + output)
└── src/
    ├── main.py                 # FastAPI app (port 7005)
    ├── orchestrator.py         # ties validate → geocode → chart → LLM
    ├── llm_client.py           # loads Gemma 4 on GPU, generates + logs
    ├── astrology_engine.py     # Swiss Ephemeris natal chart + transits
    ├── auth_advanced_astrology.py
    ├── geocoder.py             # city → lat/lon/timezone (cached + Nominatim fallback)
    ├── prompts.py              # prompt templates for story / predictions / quote
    └── validators.py           # input validation
```

## Setup

### 1. System requirements

- Linux + NVIDIA GPU
- Driver supporting **CUDA 12.8** (e.g. driver ≥ 570.x). Verify with `nvidia-smi`.
- ~8 GB free VRAM for the Gemma 4 E2B model in bfloat16.
- Python 3.10 – 3.12.

### 2. Create the virtual environment

```bash
python3 -m venv astro_daily
source astro_daily/bin/activate
```

### 3. Install PyTorch (matched to CUDA 12.8) FIRST

The cu128 wheels include Blackwell (`sm_120`, RTX 5090) kernels and
match drivers reporting CUDA 12.8.

```bash
pip install torch==2.11.0+cu128 torchvision==0.26.0+cu128 \
    --index-url https://download.pytorch.org/whl/cu128
```

### 4. Install the rest of the dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the server

```bash
python src/main.py
```

The server starts on **http://localhost:7005**. The Gemma 4 model
loads once at startup (look for `Model loaded on: cuda`).

Interactive Swagger docs: **http://localhost:7005/docs**

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/`         | Service info |
| GET  | `/status`   | Model load + CUDA status |
| GET  | `/logs`     | Recent log entries (`?type=app|gemma&limit=50`) |
| POST | `/report`   | Full astrology report (story + predictions + quote) |
| POST | `/quote`    | Daily motivational quote (today or tomorrow) |
| POST | `/sun-sign` | Fast sun-sign lookup from DOB only |

### Example requests

**Full report**
```bash
curl -X POST http://localhost:7005/report \
  -H "Content-Type: application/json" \
  -d '{"name":"Arjun Sharma","dob":"1995-05-15","tob":"10:30","place":"Jaipur"}'
```

**Tomorrow's quote**
```bash
curl -X POST http://localhost:7005/quote \
  -H "Content-Type: application/json" \
  -d '{"zodiac":"Taurus","tomorrow":true}'
```

**Quick sun sign**
```bash
curl -X POST http://localhost:7005/sun-sign \
  -H "Content-Type: application/json" \
  -d '{"dob":"1995-05-15"}'
```

**View the last 20 API calls**
```bash
curl 'http://localhost:7005/logs?type=app&limit=20'
```

**View the last 20 model calls**
```bash
curl 'http://localhost:7005/logs?type=gemma&limit=20'
```

## Logging

The server writes two append-only JSON Lines logs under `logs/`:

| File | Source | Each line records |
|---|---|---|
| `logs/app.jsonl`       | API layer ([src/main.py](src/main.py))         | `timestamp`, `endpoint`, `input`, `output`, `seconds` |
| `logs/gemma_io.jsonl`  | Model layer ([src/llm_client.py](src/llm_client.py)) | `timestamp`, `input` (prompt), `output`, `max_tokens`, `temperature`, `input_tokens`, `output_tokens`, `seconds` |

Tail the model log while the server runs:

```bash
tail -f logs/gemma_io.jsonl
```

## Notes

- **`place` is optional.** Without it the report uses sun-sign-only predictions (no ascendant, no houses).
- **Timezone is automatic** — derived from the resolved birth coordinates.
- **Geocoding cache:** common cities resolve instantly; unknown places fall back to free Nominatim (rate-limited).
- **Cost:** Gemma 4 E2B runs locally — zero per-request cost. Generation takes ~0.5–1 s per call on an RTX 5090.
- **Auto-reload:** disabled by default (`reload=False` in [src/main.py](src/main.py)) so the 4-5 GB model is loaded only once. Flip to `True` while developing if you want auto-restart.
