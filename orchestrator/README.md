# AutoGen Orchestrator (3 Agents)

Flask + AutoGen (autogen-ext) + Docker Compose の最小実装。
- Web 画面にプロンプト入力欄と 3 つのエージェント枠
- LLM で「分類 → 最適エージェント選択」
- 選択されたエージェントだけ色ハイライト
- どれにも該当しなければ一般回答（ハイライトなし）

## 開発環境での起動（コード変更自動反映）

### 🚀 推奨：ローカル開発（最速）
```bash
# 環境設定ファイルの作成
cp .env.example .env
# .env に GEMINI_API_KEY を設定（Google Generative Language API の OpenAI互換）

# 依存関係のインストール
pip install -r requirements.txt

# Flask開発サーバーの起動（自動リロード機能付き）
python run_dev.py
```

### Docker での開発（最初のセットアップ用）
```bash
# 簡単な方法
chmod +x setup-dev.sh
./setup-dev.sh

# 手動設定
cp .env.example .env
docker-compose up --build
```

## 本番環境での起動
```bash
cp .env.example .env
# .env に GEMINI_API_KEY を設定
docker-compose -f docker-compose.prod.yml up --build
```

## 機能

### 🔄 自動リロード機能（Flask開発サーバー）
- **Python コード**: ファイルを保存すると自動的にサーバーが再起動します
- **HTML テンプレート**: テンプレートファイルの変更も自動反映されます  
- **CSS/JavaScript**: 静的ファイルの変更も即座に反映されます
- **環境設定**: .env ファイルの変更も検出されます

### 📁 ファイル構成
```
orchestrator/
├── app.py              # メインのFlaskアプリケーション
├── run_dev.py          # ローカル開発用サーバー起動スクリプト
├── autogen_router.py   # AutoGenエージェントのロジック
├── templates/          # HTMLテンプレート
├── static/            # CSS, JavaScript, 画像ファイル
├── docker-compose.yml      # 開発用Docker設定（Flask開発サーバー）
├── docker-compose.prod.yml # 本番用Docker設定（Gunicorn）
└── docker-compose.dev.yml  # 従来の開発用Docker設定
```

### 🛠️ 開発時の特徴
- **Flask開発サーバー**: デフォルトで高速な開発体験を提供
- **デバッグモード**: エラー時に詳細な情報を表示
- **自動リロード**: コード変更時に自動的にサーバーが再起動
- **ホットリロード**: テンプレートや静的ファイルも即座に反映
