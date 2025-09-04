#!/bin/bash
# SungDB MCP Server 시작 스크립트

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
source venv/bin/activate

# 사용법 출력
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "사용법: $0 [--http]"
    echo ""
    echo "옵션:"
    echo "  (기본)     STDIO 모드로 실행 (MCP 클라이언트용)"
    echo "  --http     HTTP 모드로 실행 (테스트/디버깅용, Ctrl+C 지원)"
    echo "  --help     이 도움말 표시"
    exit 0
fi

# 서버 실행
echo "Starting SungDB MCP Server..."

if [[ "$1" == "--http" ]]; then
    echo "Running in HTTP mode on http://localhost:8000/mcp"
    echo "Press Ctrl+C to stop the server (works reliably in HTTP mode)"
    python sungdb_mcp.py --http
else
    echo "Running in STDIO mode for MCP client compatibility"
    echo "Press Ctrl+C to stop the server"
    echo "Note: For reliable Ctrl+C support, use: $0 --http"
    python sungdb_mcp.py
fi
