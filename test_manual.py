#!/usr/bin/env python3
"""
Manual test script for SungDB MCP Server
이 스크립트는 서버가 실행된 상태에서 테스트할 수 있습니다.
"""

import asyncio
import json
import sys
from sungdb_mcp import gdb_start, gdb_terminate, gdb_list_sessions, gdb_command, gdb_load

async def test_basic_functionality():
    """기본 기능들을 테스트합니다"""
    print("🧪 SungDB MCP Server 기본 기능 테스트 시작...")
    
    try:
        # 1. 세션 시작 테스트
        print("\n1️⃣ GDB 세션 시작 테스트...")
        start_result = await gdb_start()
        print(f"결과: {json.dumps(start_result, indent=2, ensure_ascii=False)}")
        
        if start_result["status"] != "success":
            print("❌ 세션 시작 실패!")
            return
        
        session_id = start_result["session_id"]
        print(f"✅ 세션 시작 성공! ID: {session_id}")
        
        # 2. 세션 목록 조회 테스트
        print("\n2️⃣ 활성 세션 목록 조회 테스트...")
        list_result = await gdb_list_sessions()
        print(f"결과: {json.dumps(list_result, indent=2, ensure_ascii=False)}")
        
        # 3. 기본 GDB 명령 테스트
        print("\n3️⃣ 기본 GDB 명령 테스트...")
        help_result = await gdb_command(session_id, "help")
        print(f"help 명령 결과 (일부): {help_result['output'][:200]}...")
        
        # 4. 버전 정보 테스트
        print("\n4️⃣ GDB 버전 정보 테스트...")
        version_result = await gdb_command(session_id, "show version")
        print(f"버전 정보: {version_result['output'][:100]}...")
        
        # 5. 세션 종료 테스트
        print("\n5️⃣ 세션 종료 테스트...")
        terminate_result = await gdb_terminate(session_id)
        print(f"결과: {json.dumps(terminate_result, indent=2, ensure_ascii=False)}")
        
        print("\n✅ 모든 기본 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

async def test_cortex_m_debugging():
    """Cortex-M 디버깅 워크플로우를 테스트합니다"""
    print("\n🎯 Cortex-M 디버깅 워크플로우 테스트 시작...")
    
    try:
        # ARM GDB 세션 시작
        print("\n1️⃣ ARM GDB 세션 시작...")
        start_result = await gdb_start(gdb_path="arm-none-eabi-gdb")
        
        if start_result["status"] != "success":
            print("❌ ARM GDB 세션 시작 실패! arm-none-eabi-gdb가 설치되어 있는지 확인하세요.")
            # 대안으로 일반 gdb 시도
            print("🔄 일반 gdb로 재시도...")
            start_result = await gdb_start(gdb_path="gdb")
            
        if start_result["status"] != "success":
            print("❌ GDB 세션 시작 완전 실패!")
            return
        
        session_id = start_result["session_id"]
        print(f"✅ GDB 세션 시작 성공! ID: {session_id}")
        
        # ELF 파일 경로 확인
        elf_path = "../build/cortex-m33-hello-world.elf"
        print(f"\n2️⃣ ELF 파일 로드 테스트: {elf_path}")
        
        import os
        if os.path.exists(elf_path):
            load_result = await gdb_load(session_id, elf_path)
            print(f"ELF 로드 결과: {load_result['status']}")
            if load_result["status"] == "success":
                print("✅ ELF 파일 로드 성공!")
            else:
                print(f"⚠️ ELF 파일 로드 실패: {load_result.get('output', '알 수 없는 오류')}")
        else:
            print(f"⚠️ ELF 파일을 찾을 수 없습니다: {elf_path}")
            print("먼저 'make'를 실행하여 프로젝트를 빌드하세요.")
        
        # 3. 심볼 정보 조회
        print("\n3️⃣ 심볼 정보 조회 테스트...")
        symbols_result = await gdb_command(session_id, "info functions")
        if symbols_result["status"] == "success":
            print(f"함수 목록 (일부): {symbols_result['output'][:200]}...")
        
        # 4. 아키텍처 정보 확인
        print("\n4️⃣ 아키텍처 정보 확인...")
        arch_result = await gdb_command(session_id, "show architecture")
        if arch_result["status"] == "success":
            print(f"아키텍처: {arch_result['output']}")
        
        # 세션 종료
        print("\n5️⃣ 세션 정리...")
        await gdb_terminate(session_id)
        print("✅ Cortex-M 디버깅 테스트 완료!")
        
    except Exception as e:
        print(f"❌ Cortex-M 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """메인 테스트 함수"""
    print("🚀 SungDB MCP Server 테스트 스위트")
    print("=" * 50)
    
    await test_basic_functionality()
    await test_cortex_m_debugging()
    
    print("\n" + "=" * 50)
    print("🎉 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
