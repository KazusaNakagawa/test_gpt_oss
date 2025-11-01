from __future__ import annotations

import os
import random
import re
from typing import List, Literal

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl


Role = Literal["user", "assistant"]


class Message(BaseModel):
    role: Role = Field(..., description="Message author role")
    content: str = Field(..., description="Message body")


class Reference(BaseModel):
    label: str
    url: HttpUrl


class StackRow(BaseModel):
    layer: str
    technologies: str
    benefit: str
    note: str
    source: Reference | None = None


class ChatRequest(BaseModel):
    messages: List[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    role: Role = "assistant"
    content: str


def _stack_rows() -> list[StackRow]:
    return [
        StackRow(
            layer="表示言語",
            technologies="HTML + CSS + TypeScript",
            benefit="ブラウザ標準技術で柔軟に構築できる",
            note="多くのウェブアプリで共通して採用されています。",
        ),
        StackRow(
            layer="フレームワーク／ライブラリ",
            technologies="React, Next.js",
            benefit="コンポーネントベースで SSR / SSG と組み合わせた柔軟な UI 制御に適する",
            note="有志の分析では ChatGPT 本体も React / Next.js を利用していると報告されています。",
            source=Reference(
                label="medium.com",
                url="https://medium.com/%40david.richards.tech/building-the-iconic-chatgpt-frontend-e65ec049fa54",
            ),
        ),
        StackRow(
            layer="スタイリング／UI コンポーネント",
            technologies="CSS Modules, Tailwind CSS, CSS-in-JS",
            benefit="大規模でも保守しやすいスタイリング戦略を選択できる",
            note="コミュニティでは Tailwind CSS の採用可能性が指摘されています。",
            source=Reference(
                label="reddit.com",
                url="https://www.reddit.com/r/ChatGPT/comments/12lwsii/which_programming_language_is_the_gpt_chat_app/",
            ),
        ),
        StackRow(
            layer="状態管理・通信",
            technologies="React state, Redux / Recoil, WebSocket / SSE",
            benefit="チャットのリアルタイム更新や API 通信を管理",
            note="リアルタイム性確保のため WebSocket や SSE の併用が一般的です。",
        ),
        StackRow(
            layer="SSR／ハイブリッドレンダリング",
            technologies="Next.js",
            benefit="初期描画の最適化と SEO 強化、キャッシュ戦略へ柔軟に対応",
            note="React / Next.js を核とした構成と相性が良いとされています。",
            source=Reference(
                label="medium.com",
                url="https://medium.com/%40david.richards.tech/building-the-iconic-chatgpt-frontend-e65ec049fa54",
            ),
        ),
    ]


def _fallback_reply() -> str:
    lines = [
        "良い質問ですね！",
        "このデモは TypeScript・React・Next.js のレイヤーを意識して設計しています。",
        "",
        "実際に本番環境へ展開する際は、",
        "- UI: React コンポーネントで管理しやすい構造を維持",
        "- 状態: カスタムフックや外部ストアで会話履歴を制御",
        "- 通信: API Routes や Edge Functions で OpenAI 等と連携",
        "- SSR: Next.js のハイブリッドレンダリングを活かして初期表示を最適化",
        "といった構成を検討してみてください。",
    ]
    return "\n".join(lines)


def _build_reply(message: str) -> str:
    patterns: list[tuple[re.Pattern[str], str | callable]] = [
        (
            re.compile(r"(スタック|構成|レイヤー|アーキテクチャ|architect)", re.IGNORECASE),
            "\n".join(
                [
                    "このデモは次のレイヤー構成を意識して作られています:",
                    "- 表示言語: HTML + CSS + TypeScript",
                    "- フレームワーク: React と Next.js",
                    "- スタイリング: Chakra UI をベースに Tailwind 等へ拡張しやすい構成",
                    "- 状態管理: React hooks とローカルストレージを併用",
                    "- SSR: Next.js を利用することでハイブリッドレンダリングに対応可能",
                    "",
                    "詳しい説明は docs/readme.md を確認してください。",
                ]
            ),
        ),
        (
            re.compile(r"(typescript|ts)", re.IGNORECASE),
            "TypeScript は JavaScript に型付けを導入することで、補完やリファクタリングの信頼性を高めます。Next.js でも公式にサポートされており、コンポーネント間の契約を明確にできます。",
        ),
        (
            re.compile(r"(next\.?js|nextjs|ssr|ssg)", re.IGNORECASE),
            "Next.js は SSR や SSG をシームレスに扱えるため、チャットの初期描画を高速化できます。このデモでも Next.js の App Router を前提にしています。",
        ),
        (
            re.compile(r"(レビュー|モダン|設計)", re.IGNORECASE),
            "モダンなチャットUIでは、UI層・状態層・通信層を明確に切り分けることでスケールしやすくなります。React コンポーネントを UI に、カスタムフックで状態を扱うのがシンプルで再利用性も高いアプローチです。",
        ),
        (
            re.compile(r"(stack|architecture)", re.IGNORECASE),
            lambda _: "\n".join(
                [
                    "Stack Panel で扱っている情報です:",
                    *[f"- {row.layer}: {row.technologies}" for row in _stack_rows()],
                ]
            ),
        ),
    ]

    for pattern, reply in patterns:
        if pattern.search(message):
            if callable(reply):
                return reply(message)
            return reply
    return _fallback_reply()


def _extract_prompt(request: ChatRequest) -> str | None:
    for message in reversed(request.messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


app = FastAPI(title="Chat Architect Backend", version="0.1.0")

default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
cors_origins = [
    origin.strip()
    for origin in os.getenv("CHAT_BACKEND_CORS_ORIGINS", "").split(",")
    if origin.strip()
] or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def create_chat_completion(request: ChatRequest) -> ChatResponse:
    prompt = _extract_prompt(request)
    if not prompt:
        return ChatResponse(content="まず質問や話題を入力してみてくださいね。")

    import backend.gpt as gpt
    reply_text = gpt.chat(prompt)
    # 擬似的なレスポンス生成。将来的に OpenAI 等へ差し替え可能です。
    # base_reply = _build_reply(prompt)

    # 多少のバリエーションを持たせるためにランダムなサフィックスを追加
    suffixes = [
        "",
        "\n\nもっと詳しく知りたい場合は具体的なキーワードで聞いてください。",
        "\n\n関連する技術スタックの比較についてもサポートできます。",
    ]
    suffix = random.choice(suffixes)
    # return ChatResponse(content=f"{base_reply}{suffix}")
    return ChatResponse(content=f"{reply_text}{suffix}")


@app.options("/chat")
async def chat_options() -> Response:
    """Explicitly handle CORS pre-flight checks for /chat."""
    return Response(status_code=204)
