# AutoGen Orchestrator (3 Agents)

Flask + AutoGen (autogen-ext) + Docker Compose の最小実装。
- Web 画面にプロンプト入力欄と 3 つのエージェント枠
- LLM で「分類 → 最適エージェント選択」
- 選択されたエージェントだけ色ハイライト
- どれにも該当しなければ一般回答（ハイライトなし）

## 開発環境での起動（コード変更自動反映）

### 簡単な方法
```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

### 手動設定
```bash
# 環境設定ファイルの作成
cp .env.example .env
# .env に GEMINI_API_KEY を設定（Google Generative Language API の OpenAI互換）

# 開発用Docker起動（コード変更時自動リロード）
docker-compose -f docker-compose.dev.yml up --build
```

## 本番環境での起動
```bash
cp .env.example .env
# .env に GEMINI_API_KEY を設定
docker-compose up --build
```

## 機能

### 自動リロード機能
- **Python コード**: ファイルを保存すると自動的にサーバーが再起動します
- **HTML テンプレート**: テンプレートファイルの変更も自動反映されます
- **CSS/JavaScript**: 静的ファイルの変更も即座に反映されます

### 開発時の特徴
- Flask の DEBUG モードが有効
- gunicorn の --reload オプションで Python ファイル変更を監視
- ボリュームマウントでローカルファイルの変更をコンテナ内に即座に反映
- ログレベル debug でより詳細な情報を表示
