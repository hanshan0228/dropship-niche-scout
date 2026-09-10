#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tencent Docs Direct HTTP Sync Script for Niche Research Reports.

Sends Markdown content to Tencent Docs MCP endpoint directly,
bypassing Windows command line length restrictions.
Reads authorization token dynamically from local mcporter config or environment.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def resolve_tencent_token() -> str:
    """Resolve token from environment or local mcporter config."""
    env_token = os.environ.get("TENCENT_DOCS_TOKEN", "").strip()
    if env_token:
        return env_token

    # Check local user mcporter config
    home = Path.home()
    mcporter_config = home / ".mcporter" / "mcporter.json"
    if mcporter_config.exists():
        try:
            with open(mcporter_config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                headers = cfg.get("mcpServers", {}).get("tencent-docs", {}).get("headers", {})
                auth = headers.get("Authorization", "").strip()
                if auth:
                    return auth
        except Exception:
            pass

    return ""


def sync_to_tencent_docs(title: str, markdown_content: str, token: str = "") -> dict[str, str]:
    url = "https://docs.qq.com/openapi/mcp"
    active_token = token.strip() if token else resolve_tencent_token()

    if not active_token:
        raise ValueError("Tencent Docs Authorization token not found in environment or ~/.mcporter/mcporter.json")

    # Tencent Docs title length limit (keep under 24 characters)
    clean_title = title.strip()
    if len(clean_title) > 24:
        clean_title = clean_title[:24]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_smartcanvas_by_mdx",
            "arguments": {
                "title": clean_title,
                "content_format": "markdown",
                "mdx": markdown_content
            }
        }
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": active_token,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, text/event-stream"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = resp.read().decode("utf-8")
            result = json.loads(resp_data)
            if "result" in result and "content" in result["result"]:
                inner_text = result["result"]["content"][0]["text"]
                inner_data = json.loads(inner_text)
                return {
                    "file_id": inner_data.get("file_id", ""),
                    "url": inner_data.get("url", ""),
                    "title": clean_title
                }
            elif "error" in result:
                raise RuntimeError(f"Tencent Docs MCP Error: {result['error']}")
            else:
                raise RuntimeError(f"Unexpected response: {resp_data}")
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP Error {e.code}: {error_msg}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync report to Tencent Docs")
    parser.add_argument("--title", type=str, required=True, help="Title of the Tencent Doc")
    parser.add_argument("--file", type=str, required=True, help="Path to the markdown file to sync")
    parser.add_argument("--token", type=str, default="", help="Optional Tencent Docs API token")

    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        res = sync_to_tencent_docs(title=args.title, markdown_content=content, token=args.token)
        print("SUCCESS")
        print(f"FILE_ID: {res['file_id']}")
        print(f"URL: {res['url']}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
