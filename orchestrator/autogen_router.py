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
import re
from typing import Dict, Literal

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import SystemMessage, UserMessage

load_dotenv()

AgentKey = Literal["coder", "analyst", "travel", "none"]

CLASSIFIER_SYSTEM = """あなたは専門的なルーティング分類器です。ユーザーの質問を以下の専門エージェントのいずれかに分類してください:

**coder** - 以下の場合に選択:
- プログラミング言語、コード作成、デバッグ、実装
- ソフトウェア設計、アーキテクチャ、システム構築
- フレームワーク、ライブラリ、API開発
- データベース設計、Web開発、アプリ開発
- デプロイメント、CI/CD、DevOps

**analyst** - 以下の場合に選択:
- データ分析、統計処理、機械学習
- 研究方法論、実験設計、仮説検証
- ビジネス分析、市場調査、競合分析
- データ可視化、レポート作成
- 学術的調査、論文関連、エビデンス分析

**travel** - 以下の場合に選択:
- 旅行計画、観光ルート、宿泊施設
- 交通手段、移動方法、アクセス情報
- 地域ガイド、現地情報、文化・歴史
- 旅行の準備、持ち物、予算計画
- グルメ、ショッピング、アクティビティ

**none** - 上記のどれにも明確に当てはまらない一般的な質問

必ずJSON形式で回答してください:
{"label": "coder"}
{"label": "analyst"}  
{"label": "travel"}
{"label": "none"}

この4つの形式のいずれか1つのみを出力してください。"""

AGENT_SYSTEMS: Dict[str, str] = {
    "coder": (
        "あなたは経験豊富なソフトウェアエンジニア・アーキテクトです。\n"
        "【あなたの専門分野】\n"
        "- プログラミング言語（Python、JavaScript、Java、Go等）\n"
        "- Web開発（フロントエンド・バックエンド）\n"
        "- システム設計・マイクロサービス・API設計\n"
        "- データベース設計・クエリ最適化\n"
        "- DevOps・CI/CD・クラウド技術\n\n"
        "【回答方針】\n"
        "1. 具体的なコード例を含めて説明する\n"
        "2. ベストプラクティスとセキュリティを考慮する\n"
        "3. 実装手順を段階的に示す\n"
        "4. 必要に応じて代替案も提示する\n\n"
        "技術的な質問に対して、実用的で信頼性の高いソリューションを提供してください。"
    ),
    "analyst": (
        "あなたは専門的なデータアナリスト・研究者です。\n"
        "【あなたの専門分野】\n"
        "- データ分析・統計解析・機械学習\n"
        "- 実験設計・仮説検証・A/Bテスト\n"
        "- ビジネス分析・市場調査・競合分析\n"
        "- データ可視化・ダッシュボード作成\n"
        "- 学術研究・論文分析・エビデンス評価\n\n"
        "【回答方針】\n"
        "1. データに基づく客観的な分析を行う\n"
        "2. 統計的手法や分析アプローチを明示する\n"
        "3. 仮定・制約・限界を明確に説明する\n"
        "4. 可視化や具体的な分析例を提示する\n\n"
        "分析的思考を重視し、エビデンスに基づいた洞察を提供してください。"
    ),
    "travel": (
        "あなたは経験豊富な旅行プランナー・観光ガイドです。\n"
        "【あなたの専門分野】\n"
        "- 旅行プラン作成・ルート最適化\n"
        "- 宿泊施設・交通手段の選択\n"
        "- 地域情報・文化・歴史・グルメ\n"
        "- 予算管理・旅行準備・必要な手続き\n"
        "- 季節性・混雑状況・穴場スポット\n\n"
        "【回答方針】\n"
        "1. 具体的な行程表・スケジュールを提示する\n"
        "2. 予算・所要時間・アクセス方法を明記する\n"
        "3. 実用的なアドバイス・注意点を含める\n"
        "4. 代替案・プランBも用意する\n\n"
        "旅行者のニーズに合わせて、実現可能で魅力的な旅行体験を提案してください。"
    ),
    "general": (
        "あなたは知識豊富で親しみやすい汎用アシスタントです。\n"
        "【対応範囲】\n"
        "- 一般的な質問・日常的な相談\n"
        "- 概念の説明・用語の定義\n"
        "- 生活に役立つ情報・アドバイス\n"
        "- クリエイティブな相談・アイデア提案\n\n"
        "【回答方針】\n"
        "1. 分かりやすく親しみやすい口調で回答する\n"
        "2. 具体例や身近な例を使って説明する\n"
        "3. 必要に応じて複数の視点を提示する\n"
        "4. 追加の質問や確認を促す\n\n"
        "ユーザーの質問に真摯に向き合い、役立つ情報を提供してください。"
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

def clean_response_content(content: str) -> str:
    """Clean response content from API metadata"""
    if not content:
        return ""
    
    # Remove common API metadata patterns
    content = re.sub(r"finish_reason\s*=\s*['\"][^'\"]*['\"]", "", content)
    content = re.sub(r"usage\s*=\s*RequestUsage\([^)]*\)", "", content)
    content = re.sub(r"\b(cached|logprobs|thought)\s*=\s*[^,\s]+", "", content)
    content = re.sub(r"content\s*=\s*", "", content)
    content = re.sub(r"\[([^\]]+)\]\(https?://[^\s)]*$", r"\1", content)
    
    # Clean up extra commas and spaces
    content = re.sub(r",\s*,", ",", content)
    content = re.sub(r"\s+", " ", content)
    content = content.strip()
    
    return content

class Orchestrator:
    def __init__(self):
        self.client = build_model_client()

    async def _chat(self, system: str, user: str) -> str:
        """
        Create a single turn conversation with autogen-ext OpenAI compatible client.
        Clean API metadata from the response.
        """
        resp = await self.client.create(
            messages=[
                SystemMessage(content=system),
                UserMessage(content=user, source="user"),
            ],
        )
        # OpenAI compatible response format: choices[0].message.content
        try:
            content = resp.choices[0].message.get("content") or ""
            return clean_response_content(content.strip())
        except Exception:
            # Fallback for library differences - also clean metadata
            fallback_content = str(resp)
            return clean_response_content(fallback_content)

    async def classify_async(self, prompt: str) -> AgentKey:
        """
        Classify prompt into agent type.
        Implements robust JSON parsing and fallback logic.
        """
        try:
            raw = await self._chat(CLASSIFIER_SYSTEM, prompt)
            print(f"Classifier raw response: {raw}")  # Debug log
            
            # Multiple JSON parsing attempts
            label = "none"
            
            # 1. Standard JSON parsing
            try:
                data = json.loads(raw)
                lbl = (data.get("label") or "").strip().lower()
                if lbl in ("coder", "analyst", "travel", "none"):
                    label = lbl
                    print(f"Classification successful (JSON): {label}")
                    return label  # type: ignore[return-value]
            except json.JSONDecodeError:
                pass
            
            # 2. Pattern matching if JSON fails
            raw_lower = raw.lower()
            if '"coder"' in raw_lower or 'coder' in raw_lower:
                label = "coder"
            elif '"analyst"' in raw_lower or 'analyst' in raw_lower:
                label = "analyst"
            elif '"travel"' in raw_lower or 'travel' in raw_lower:
                label = "travel"
            else:
                # 3. Keyword-based fallback classification
                prompt_lower = prompt.lower()
                
                # Programming related keywords
                coding_keywords = [
                    "コード", "プログラム", "実装", "開発", "設計", "python", "javascript", 
                    "java", "api", "データベース", "web", "アプリ", "システム", "サーバー",
                    "フレームワーク", "ライブラリ", "バグ", "デバッグ", "deploy", "git"
                ]
                
                # Analysis related keywords
                analysis_keywords = [
                    "分析", "統計", "データ", "機械学習", "研究", "実験", "調査", "可視化",
                    "グラフ", "レポート", "検証", "仮説", "エビデンス", "競合", "市場"
                ]
                
                # Travel related keywords
                travel_keywords = [
                    "旅行", "観光", "宿泊", "ホテル", "交通", "電車", "飛行機", "ルート",
                    "プラン", "予算", "グルメ", "レストラン", "スポット", "地域", "文化"
                ]
                
                # Keyword matching
                coding_score = sum(1 for kw in coding_keywords if kw in prompt_lower)
                analysis_score = sum(1 for kw in analysis_keywords if kw in prompt_lower)
                travel_score = sum(1 for kw in travel_keywords if kw in prompt_lower)
                
                print(f"Keyword scores - coding: {coding_score}, analysis: {analysis_score}, travel: {travel_score}")
                
                if coding_score > 0 and coding_score >= analysis_score and coding_score >= travel_score:
                    label = "coder"
                elif analysis_score > 0 and analysis_score >= travel_score:
                    label = "analyst"
                elif travel_score > 0:
                    label = "travel"
                else:
                    label = "none"
            
            print(f"Final classification: {label}")
            return label  # type: ignore[return-value]
            
        except Exception as e:
            print(f"Classification error: {e}")
            return "none"

    async def answer_with_agent_async(self, agent: AgentKey, prompt: str) -> str:
        """
        Generate answer using the specified agent.
        """
        if agent in ("coder", "analyst", "travel"):
            system = AGENT_SYSTEMS[agent]
        else:
            system = AGENT_SYSTEMS["general"]
        
        try:
            response = await self._chat(system, prompt)
            
            # Include agent identification in response (for debugging)
            if agent != "none":
                agent_names = {
                    "coder": "ソフトウェアエンジニア",
                    "analyst": "データアナリスト",
                    "travel": "旅行プランナー"
                }
                agent_name = agent_names.get(agent, "専門エージェント")
                # Add agent info to end of response (can be processed by UI later)
                response += f"\n\n---\n【回答者: {agent_name}】"
            
            return response
            
        except Exception as e:
            print(f"Answer generation error for agent {agent}: {e}")
            return f"Sorry, an error occurred while generating response from {agent} agent."

    async def ask_async(self, prompt: str) -> Dict[str, str]:
        """
        Routing -> Answer generation
        returns: {"selected": "...", "response": "..."}
        """
        print(f"Processing prompt: {prompt}")
        
        # Classification
        agent: AgentKey = await self.classify_async(prompt)
        print(f"Classified as: {agent}")
        
        # Answer generation
        answer = await self.answer_with_agent_async(agent, prompt)
        print(f"Response generated by {agent} agent")
        
        return {
            "selected": agent, 
            "response": answer
        }

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
