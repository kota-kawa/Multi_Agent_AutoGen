
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from autogen_router import Orchestrator

load_dotenv()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# プロセス起動時に Orchestrator を初期化（クライアントは使い回す）
orchestrator = Orchestrator()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/ask")
def api_ask():
    data = request.get_json(force=True, silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    try:
        # 同期ルートから安全に実行
        result = asyncio.run(orchestrator.ask_async(prompt))
        # result: {"selected": "coder"/"analyst"/"travel"/"none", "response": "..."}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    # 開発ローカル用: flask run と同様（Docker本番は gunicorn）
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("FLASK_ENV") == "development")
