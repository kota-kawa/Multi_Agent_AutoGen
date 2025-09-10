#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoGen (autogen-ext) を用いて:
1) プロンプトを 3 クラス（coder / analyst / travel）+ none に分類
2) 該当エージェントの「役割(System指示)」で 1ターン回答を生成
3) none のときは一般回答（ハイライトなし）

- 依存: autogen-ext==0.4.7
- LLM 接続は Gemini(OpenAI互換API) を既定。環境変数で設定。
"""

import os
import json
import asyncio
from typing import Dict, Literal

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

AgentKey = Literal["coder", "analyst", "travel", "none"]

CLASSIFIER_SYSTEM = """あなたは高度なルーティング用分類器です。
次のユーザープロンプトを、下記のいずれか1つに厳密に分類してください:
- "coder": プログラミング、アーキテクチャ設計、コード修正/生成/デプロイ/LLMエージェント実装 等
- "analyst": データ分析、統計、学術調査、実験設計、可視化、論文的解説 等
- "travel": 旅行計画、観光、宿/交通、地域ガイド、ライフハック実務 等
- "none": 上記のいずれにもはっきり当てはまらない場合

出力は必ず次のJSON1行のみ:
{"label":"coder|analyst|travel|none"}"""

AGENT_SYSTEMS: Dict[str, str] = {
    "coder": (
        "あなたはプロフェッショナルなソフトウェアアーキテクト/フルスタックエンジニアです。"
        "要件定義→設計→実装→デプロイまで一貫して具体的に提案・コード生成を行います。"
        "箇条書きで手順を明確化し、実用的で堅牢なサンプルコードを提示してください。"
    ),
    "analyst": (
        "あなたはエビデンスドリブンなデータアナリスト/研究者です。"
        "データ仮定、手法選定、統計的妥当性、限界やバイアスを明示し、"
        "根拠ある結論と次アクションを簡潔に示してください。"
    ),
    "travel": (
        "あなたは実務に強い旅行プランナーです。"
        "条件整理→行程案→費用/所要時間/注意点→代替案まで、"
        "現実的かつわかりやすく提示してください。"
    ),
    "general": (
        "あなたは誠実で有能な汎用アシスタントです。"
        "ユーザーの質問意図を丁寧に汲み取り、具体的で実行可能な回答を簡潔に示してください。"
    ),
}

def build_model_client() -> OpenAIChatCompletionClient:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) is required")

    base_url = os.environ.get(
        "GEMINI_OPENAI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    # v0.4.7+ で family 指定が必須
    client = OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "structured_output": False,
            "family": "gemini",
        },
        max_tokens=2048,
    )
    return client

class Orchestrator:
    def __init__(self):
        self.client = build_model_client()

    async def _chat(self, system: str, user: str) -> str:
        """
        autogen-ext の OpenAI 互換クライアントで 1ターン会話。
        """
        resp = await self.client.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        # OpenAI互換の想定: choices[0].message.content
        try:
            return (resp.choices[0].message.get("content") or "").strip()
        except Exception:
            # 念のためフォールバック（ライブラリの差異を吸収）
            return str(resp)

    async def classify_async(self, prompt: str) -> AgentKey:
        raw = await self._chat(CLASSIFIER_SYSTEM, prompt)
        label = "none"
        try:
            data = json.loads(raw)
            lbl = (data.get("label") or "").strip().lower()
            if lbl in ("coder", "analyst", "travel", "none"):
                label = lbl
        except Exception:
            # JSON化失敗 → none
            label = "none"
        return label  # type: ignore[return-value]

    async def answer_with_agent_async(self, agent: AgentKey, prompt: str) -> str:
        if agent in ("coder", "analyst", "travel"):
            system = AGENT_SYSTEMS[agent]
        else:
            system = AGENT_SYSTEMS["general"]
        return await self._chat(system, prompt)

    async def ask_async(self, prompt: str) -> Dict[str, str]:
        """
        ルーティング → 回答生成
        returns: {"selected": "...", "response": "..."}
        """
        agent: AgentKey = await self.classify_async(prompt)
        answer = await self.answer_with_agent_async(agent, prompt)
        return {"selected": agent, "response": answer}

    async def close(self):
        try:
            await self.client.close()
        except Exception:
            pass

# 単体テスト用
if __name__ == "__main__":
    orch = Orchestrator()
    out = asyncio.run(orch.ask_async("週末に京都で歴史を感じる半日観光プランを作って"))
    print(out)
    asyncio.run(orch.close())
