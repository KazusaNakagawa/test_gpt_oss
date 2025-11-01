from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("CHAT_BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("CHAT_BACKEND_PORT", "8000"))
    reload = os.getenv("CHAT_BACKEND_RELOAD", "true").lower() in {"1", "true", "yes"}

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )


if __name__ == "__main__":
  main()
