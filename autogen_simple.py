#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAIライブラリ互換のエンドポイント経由で Gemini を利用し、
Microsoft AutoGen の RoundRobinGroupChat で
異なる分野の専門家2名（経済学/気候科学）が議論→合意するサンプル。

主なポイント:
- 終了条件: 「【結論】」のテキスト一致 かつ 発話者が専門家のときのみ停止
  （TextMentionTermination AND SourceMatchTermination の合成）
- ユーザー文に「【結論】」が含まれても止まらない
- Gemini の OpenAI互換APIを使用（base_url を Google の互換URLに設定）
- model_info に family を含む必須フィールドを明示（v0.4.7+の厳格化に対応）
- AutoGen/OpenAIの仕様に合わせ、エージェント name は ASCII の英数字・_・- のみ使用
- ★発言ごとに print するストリーミング表示（run_stream）を実装
- ★重複ユーザー表示と空メッセージ表示を抑止
"""

import os
import asyncio
from typing import List, Optional

# （任意）.env を自動読み込み（未インストールでも動くようにtry）
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import (
    TextMentionTermination,
    MaxMessageTermination,
    SourceMatchTermination,
)
from autogen_agentchat.messages import BaseChatMessage


def build_model_client() -> OpenAIChatCompletionClient:
    """Gemini(OpenAI互換) クライアントを構築"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini APIキーが見つかりません。環境変数 GEMINI_API_KEY (または GOOGLE_API_KEY) を設定してください。"
        )

    base_url = os.environ.get(
        "GEMINI_OPENAI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    # 既定モデルは環境に合わせて任意。ここでは 2.5 系を想定（2.0 系でも可）。
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    # 非OpenAIモデルを OpenAI互換で使うために base_url と model_info を指定
    # v0.4.7+ では family を含む必須フィールドが厳密化されている。
    model_client = OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "structured_output": False,
            "family": "gemini",  # 必須: v0.4.7+ で未指定は例外
        },
        temperature=0.7,
        max_tokens=2048,  # ★ 途切れを減らすため増量
    )
    return model_client


def build_agents(model_client: OpenAIChatCompletionClient) -> List[AssistantAgent]:
    """2名の専門家エージェント（異分野）を作成"""

    # ※ OpenAI/AutoGen の name 制約に合わせ ASCII のみを使用
    #   表示は後段の label_map で日本語に変換して出力。
    economist = AssistantAgent(
        name="economist",
        model_client=model_client,
        system_message=(
            "あなたはマクロ経済・公共政策の教授です。政策評価（費用便益分析）、"
            "税制設計、労働市場の一般均衡効果に精通しています。"
            "主張には定量的根拠や参考値（概算）を示し、前提を明記してください。"
            "冗長さは避け、要点を短くまとめて発言します。"
            "最終ターンに限り、合意が形成できたと判断したら、最後の1行を"
            "『【結論】…』で始めて簡潔に書きなさい。"
        ),
    )

    climatologist = AssistantAgent(
        name="climatologist",
        model_client=model_client,
        system_message=(
            "あなたは気候科学・環境工学の専門家です。温室効果ガス排出、"
            "交通起源排出量の推計、ライフサイクル影響評価に精通しています。"
            "不確実性と前提条件を明確化し、科学的妥当性を重視して発言します。"
            "冗長さは避け、要点を短くまとめて発言します。"
            "最終ターンに限り、合意が形成できたと判断したら、最後の1行を"
            "『【結論】…』で始めて簡潔に書きなさい。"
        ),
    )

    return [economist, climatologist]


async def run_discussion() -> None:
    """2名の専門家にラウンドロビンで議論させ、最後に【結論】で締める（発言ごとに即時表示）"""
    model_client = build_model_client()
    agents = build_agents(model_client)

    # ---------------- 終了条件 ----------------
    # 「【結論】」という文字列が *かつ* 発話者が専門家（=ユーザー以外）の時だけ停止。
    text_done = TextMentionTermination("【結論】")
    by_agent = SourceMatchTermination("economist") | SourceMatchTermination("climatologist")
    termination = (text_done & by_agent) | MaxMessageTermination(16)
    # ------------------------------------------

    team = RoundRobinGroupChat(
        participants=agents,
        termination_condition=termination,
        max_turns=24,  # セーフティ上限
    )

    # 議題（ユーザー文側には『【結論】』のリテラルを含めない）
    task = (
        "議題: 大都市圏で2030年までに道路渋滞を30%削減する施策を検討しなさい。"
        "各自の専門性（経済学/気候科学）の観点から、2〜4ターンで要点を出し合い、"
        "最終的に合意の“結論”を1行で提示してください。"
        "結論は政策の組み合わせ（例: 料金施策×需要抑制×代替手段強化）を含み、"
        "実現可能性と副作用に触れて簡潔に書きなさい。"
    )

    # 表示ラベル（日本語）に変換
    label_map = {
        "economist": "経済学者",
        "climatologist": "気候科学者",
        "user": "user",
        "system": "system",
    }

    print("\n================ 会話ログ（逐次） ================\n")

    # 【逐次表示】run_stream で各メッセージ確定ごとに出力
    last_conclusion_author: Optional[str] = None
    seen_first_user: bool = False

    async for message in team.run_stream(task=task):
        if not isinstance(message, BaseChatMessage):
            # イベントやエラーオブジェクトなどはスキップ
            continue

        source = getattr(message, "source", "unknown")
        # content の取り出しは to_text() を優先
        content = ""
        try:
            text = message.to_text()  # type: ignore[attr-defined]
            if isinstance(text, str):
                content = text
        except Exception:
            # to_text が無い型は content を使用
            content = getattr(message, "content", "")

        # 空メッセージは表示しない
        if not isinstance(content, str) or not content.strip():
            continue

        # ユーザー議題の重複回避:
        # stream 側からの最初の user メッセージだけ表示（自前の先行 print はしない）
        if source == "user":
            if seen_first_user:
                continue
            seen_first_user = True

        jp = label_map.get(source, source)
        print(f"[{jp}] {content}")

        if "【結論】" in content and source in ("economist", "climatologist"):
            last_conclusion_author = source

    # 終了情報（簡易推定）
    print("\n================ 停止情報 ================\n")
    if last_conclusion_author:
        print(f"stop_reason: Text '【結論】' mentioned by {label_map.get(last_conclusion_author, last_conclusion_author)}")
    else:
        print("stop_reason: （推定不能。最大メッセージ上限、またはその他の終了条件の可能性）")

    print("\n================ 実行完了 ================\n")

    # 後片付け
    try:
        await model_client.close()
    except Exception:
        pass


def main() -> None:
    asyncio.run(run_discussion())


if __name__ == "__main__":
    main()
