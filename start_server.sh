#!/bin/bash
# SungDB MCP Server 시작 스크립트

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
source venv/bin/activate

# 서버 실행
echo "Starting SungDB MCP Server..."
echo "Press Ctrl+C to stop the server"
python sungdb_mcp.py
