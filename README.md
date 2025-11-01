# GPT OSS Utilities

This repository now houses two related utilities:

1. **FastAPI chat backend** (`backend/`) that serves deterministic demo responses for a ChatGPT-style UI. Point your frontend (for example the `test_chatapp_codex` Next.js app) at this service instead of booting a backend inside the frontend repository.
2. **Transformers smoke test** (`main.py`) for verifying that open-weight Hugging Face chat models can be downloaded and executed locally.

Use whichever component you need; they are independent.

---

## FastAPI Chat Backend

### Features
- `POST /chat` accepts full conversation history and returns an assistant reply built from stack-aware heuristics (matching the behaviour of the original frontend demo).
- `GET /health` returns a simple status payload.
- CORS support with configurable allowlist via `CHAT_BACKEND_CORS_ORIGINS`.
- Easy local launch with `python -m backend` (uses Uvicorn under the hood).

### Requirements
- Python 3.10+

Install dependencies inside a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Running the server

```bash
# inside the virtual environment
python -m backend
# or explicitly:
# uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Environment variables:

- `CHAT_BACKEND_HOST` (default `0.0.0.0`)
- `CHAT_BACKEND_PORT` (default `8000`)
- `CHAT_BACKEND_RELOAD` (`true`/`false`, controls Uvicorn reload in `python -m backend`)
- `CHAT_BACKEND_CORS_ORIGINS` (comma-separated list, defaults to `http://localhost:3000,http://127.0.0.1:3000`)

### API quick reference

- `GET /health` → `{"status": "ok"}`
- `POST /chat`

  ```jsonc
  {
    "messages": [
      {"role": "assistant", "content": "..."},
      {"role": "user", "content": "Next.js って何が良いの？"}
    ]
  }
  ```

  Response:

  ```jsonc
  {"role": "assistant", "content": "Next.js は SSR や SSG をシームレスに扱えるため..."}
  ```

The endpoint mirrors the API the frontend previously emulated on the client, so no schema changes are required on the consumer side. Configure your frontend with `NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000` (or another host/port) and ensure the origin is listed in `CHAT_BACKEND_CORS_ORIGINS`.

---

## Transformers Smoke Test (`main.py`)

This script remains available for quickly checking whether a Hugging Face chat model can run on your machine.

### Requirements
- Python 3.10+ (tested with 3.13)
- Network access to Hugging Face unless the model is cached
- Adequate RAM/VRAM for the target model

Install dependencies (they include PyTorch, Transformers, etc.):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Update `config/model.json`:

```json
{
  "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
  "role": "user",
  "content": "Hello, how are you?"
}
```

- `model_id`: Hugging Face repo ID (public/gated as appropriate)
- `role`: Role applied to the prompt (`user` by default)
- `content`: Prompt to send

### Running

```bash
source .venv/bin/activate
python main.py
```

Example output:

```
Device set to use mps
{'role': 'assistant', 'content': "I am fine, thank you. How about you? Is everything okay? Yes, I'm doing well."}
```

The printed dictionary is the assistant turn returned by the pipeline. Adjust generation parameters inside `main.py` (`max_new_tokens`, `temperature`, etc.) as needed.

### Troubleshooting
- **401 Unauthorized / gated model**: Use a public model or authenticate with `huggingface-cli`.
- **Out-of-memory errors**: Choose a smaller model, reduce `max_new_tokens`, or set `device_map="cpu"`.
- **Slow downloads**: Model artifacts cache under `~/.cache/huggingface` for reuse.

### Notes
- Apple Silicon devices leverage Metal (`mps`) automatically.
- The `output/` directory contains example generations for reference only.
