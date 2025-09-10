# AutoGen Orchestrator (3 Agents)

Flask + AutoGen (autogen-ext) + Docker Compose の最小実装。
- Web 画面にプロンプト入力欄と 3 つのエージェント枠
- LLM で「分類 → 最適エージェント選択」
- 選択されたエージェントだけ色ハイライト
- どれにも該当しなければ一般回答（ハイライトなし）

## 開発環境での起動（Flask開発サーバー、コード変更自動反映）

### 最も簡単な方法（Flask開発サーバー）
```bash
# 必要なパッケージをインストール
pip3 install Flask python-dotenv

# Flask開発サーバーを起動（自動リロード有効）
./run-dev.sh
```

### 手動でFlask開発サーバーを起動
```bash
# 環境変数を設定してFlask開発サーバーを起動
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 app.py
```

### Docker での開発環境
```bash
# 環境設定ファイルの作成
cp .env.example .env
# .env に GEMINI_API_KEY を設定（Google Generative Language API の OpenAI互換）

# 開発用Docker起動（Flask開発サーバー使用、コード変更時自動リロード）
docker-compose -f docker-compose.dev.yml up --build
```

## 本番環境での起動
```bash
cp .env.example .env
# .env に GEMINI_API_KEY を設定
docker-compose up --build
```

## 機能

### 自動リロード機能（Flask開発サーバー）
- **Python コード**: ファイルを保存すると自動的にサーバーが再起動します
- **HTML テンプレート**: テンプレートファイルの変更も自動反映されます
- **CSS/JavaScript**: 静的ファイルの変更も即座に反映されます

### 開発時の特徴
- Flask の DEBUG モードが有効
- Flask開発サーバーの自動リロード機能で Python ファイル変更を監視
- ボリュームマウントでローカルファイルの変更をコンテナ内に即座に反映
- デバッガーが有効でエラー時に詳細な情報を表示
