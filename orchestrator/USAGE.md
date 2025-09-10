# 自動リロード機能使用方法

このDockerセットアップでは、コードを変更すると自動的に反映される開発環境を提供します。

## 使用方法

### 1. 簡単セットアップ（推奨）

```bash
cd orchestrator
chmod +x setup-dev.sh
./setup-dev.sh
```

このスクリプトが実行する内容:
- `.env` ファイルが存在しない場合、`.env.example` からコピー
- 開発用Dockerイメージをビルド  
- 自動リロード有効な開発サーバーを起動

### 2. 手動セットアップ

```bash
cd orchestrator

# 環境設定
cp .env.example .env
# .env ファイルを編集してAPIキーを設定

# 開発環境での起動（Flask直接実行）
docker compose -f docker-compose.dev.yml up --build

# または本番環境（gunicorn使用）  
docker compose up --build
```

## 自動リロード機能の詳細

### 監視対象ファイル
- **Python ファイル** (`.py`): 保存時に自動的にサーバー再起動
- **HTMLテンプレート** (`templates/*.html`): 保存時に即座に反映
- **CSS/JavaScript** (`static/*`): ブラウザキャッシュを無効化して即座に反映

### 動作確認方法

1. サーバー起動後 `http://localhost:8000/status` にアクセス
   ```json
   {
     "auto_reload": true,
     "debug_mode": true,
     "message": "Auto-reload is working! ..."
   }
   ```

2. `app.py` ファイルを編集して保存
3. ログにリロードメッセージが表示される:
   ```
   * Detected change in '/app/app.py', reloading
   * Restarting with stat
   ```

4. 変更が即座に反映されることを確認

## 開発とプロダクション

### 開発環境の特徴
- `docker-compose.dev.yml`: Flask直接実行、より高速なリロード
- `docker-compose.yml`: gunicornでの実行、本番に近い環境

### 環境変数
```bash
FLASK_ENV=development    # 開発モード有効
FLASK_DEBUG=1           # デバッグモード有効
PYTHONDONTWRITEBYTECODE=1  # .pyc ファイル生成無効
PYTHONUNBUFFERED=1      # Python出力をバッファリングしない
```

## トラブルシューティング

### ポート8000が使用中の場合
```bash
docker compose down
# または異なるポートを使用
docker compose up -p 8001:8000
```

### AutoGenの依存関係が見つからない場合
アプリケーションはモック実装でフォールバックし、基本的な自動リロード機能は動作します。
完全な機能を使用するには、AutoGenの依存関係をインストールしてください。

### ファイル変更が反映されない場合
1. Dockerボリュームマウントを確認: `./:/app`
2. ファイル権限を確認
3. コンテナを再起動: `docker compose restart`