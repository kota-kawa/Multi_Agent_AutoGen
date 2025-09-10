#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Try to import autogen_router, fall back to mock implementation if not available
try:
    from autogen_router import Orchestrator
    AUTOGEN_AVAILABLE = True
except ImportError:
    print("Warning: autogen_router not available. Using mock implementation for development.")
    AUTOGEN_AVAILABLE = False
    
    class MockOrchestrator:
        async def ask_async(self, prompt):
            return {
                "selected": "none",
                "response": f"Mock response for development: '{prompt}'. AutoGen dependencies need to be installed for full functionality."
            }

load_dotenv()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# プロセス起動時に Orchestrator を初期化（クライアントは使い回す）
if AUTOGEN_AVAILABLE:
    orchestrator = Orchestrator()
else:
    orchestrator = MockOrchestrator()

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
    return "ok - auto-reload verified!", 200

@app.get("/status")
def status():
    return jsonify({
        "autogen_available": AUTOGEN_AVAILABLE,
        "debug_mode": app.debug,
        "auto_reload": app.config.get("TEMPLATES_AUTO_RELOAD", False),
        "message": "Auto-reload is working! Code changes are automatically reflected! 自動リロード機能が動作中です！"
    })

if __name__ == "__main__":
    # 開発ローカル用:flask run と同様（Docker本番は gunicorn）
    debug_mode = os.getenv("FLASK_ENV") == "development" or os.getenv("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode, use_reloader=debug_mode)
