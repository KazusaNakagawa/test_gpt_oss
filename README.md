# GPT OSS Test Runner

## Overview
This repository contains a minimal script (`main.py`) for smoke-testing open weight LLMs via the Hugging Face [`transformers`](https://huggingface.co/docs/transformers) pipeline. It is currently exercised on an Apple Mac with M4 SoC and runs fine within that environment. The script:

- reads `config/model.json` to determine which chat model to load and what prompt to send
- automatically selects the best available device (`mps`, GPU, or CPU) through `device_map="auto"`
- prints the model's assistant reply to STDOUT so you can verify the model is responding

Use it to quickly check whether a chosen model ID can be downloaded and executed on your local machine.

## Requirements
- Python 3.10+ (tested with 3.13 inside a virtual environment)
- An active internet connection to download models from Hugging Face (unless already cached)
- Sufficient RAM/VRAM to host the model you choose

Install Python dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Edit `config/model.json` to point at any Hugging Face chat model you have access to. The repository ships with the configuration set to the TinyLlama model that has been verified to run on the above Mac M4 environment:

```json
{
    "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "role": "user",
    "content": "Hello, how are you?"
}
```

- `model_id`: Hugging Face repository ID. Pick a fully public model (for example `TinyLlama/TinyLlama-1.1B-Chat-v1.0`, `microsoft/phi-2`, `princeton-nlp/Sheared-Llama-1.3B`). Gated or private repositories require logging in with `huggingface-cli login` or setting `HF_TOKEN`. The default value (`TinyLlama/TinyLlama-1.1B-Chat-v1.0`) is the one confirmed to run in this project.
- `role`: The role applied to the incoming message (usually `user`).
- `content`: The text prompt to send.

## Running
After configuration and dependency installation:

```bash
source .venv/bin/activate
python main.py
```

Typical output on an Apple Silicon machine looks like:

```
Device set to use mps
{'role': 'assistant', 'content': "I am fine, thank you. How about you? Is everything okay? Yes, I'm doing well."}
```

The dictionary printed is the final turn in the generated conversation (`role` and `content` keys). Adjust generation behaviour by editing the parameters passed to `pipeline` in `main.py` (for example `max_new_tokens`, `temperature`, or `return_full_text`).

## Troubleshooting
- **401 Unauthorized / gated model**: Choose a public model or authenticate with Hugging Face (`huggingface-cli login`).
- **Out-of-memory errors**: Switch to a smaller model ID, reduce `max_new_tokens`, or force CPU execution by replacing `device_map="auto"` with `"cpu"`.
- **Slow downloads**: Model artifacts are cached under `~/.cache/huggingface`. Once downloaded, reruns are fast as long as the cache remains.

## Notes
- Apple Silicon devices with recent PyTorch will automatically use Metal (`mps`). On other hardware the pipeline falls back to CUDA or CPU.
- The repository includes an `output/` folder with sample generations; it is not used by the script but retained for reference.
