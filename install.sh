#!/bin/bash
set -e

echo "🚀 SungDB MCP Server 설치 시작..."

# Python 가상환경 생성
echo "📦 Python 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
echo "📋 의존성 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 패키지 설치
echo "🔧 SungDB MCP 서버 설치 중..."
pip install -e .

echo "✅ 설치 완료!"
echo ""
echo "🎯 사용법:"
echo "  1. 가상환경 활성화: source venv/bin/activate"
echo "  2. 서버 실행: python sungdb_mcp.py"
echo "  3. 또는: sungdb-mcp"
echo ""
echo "📖 자세한 사용법은 README.md를 참조하세요."
