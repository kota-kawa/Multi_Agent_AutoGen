# AutoGen Orchestrator (3 Agents)

Flask + AutoGen (autogen-ext) + Docker Compose の最小実装。
- Web 画面にプロンプト入力欄と 3 つのエージェント枠
- LLM で「分類 → 最適エージェント選択」
- 選択されたエージェントだけ色ハイライト
- どれにも該当しなければ一般回答（ハイライトなし）

## 起動

```bash
cp .env.example .env
# .env に GEMINI_API_KEY を設定（Google Generative Language API の OpenAI互換）
docker compose up --build
