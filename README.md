# 🔧 SungDB MCP Server

**FastMCP 기반의 고성능 GDB 디버깅 서버**

기존 GDB MCP의 동작 불안정 문제를 해결하기 위해 FastMCP를 활용하여 구현한 새로운 GDB MCP 서버입니다. Python으로 GDB 프로세스를 관리하고 명령을 큐잉하여 순차적으로 실행하는 안정적인 디버깅 환경을 제공합니다.

## ✨ 주요 특징

- **🚀 FastMCP 기반**: 최신 FastMCP 프레임워크로 구현된 고성능 서버
- **🔄 명령 큐잉**: 명령어들을 큐에 저장하여 순차적으로 안전하게 실행
- **🎯 세션 관리**: 여러 GDB 세션을 동시에 관리 가능
- **⚡ 비동기 처리**: asyncio 기반의 비동기 명령 처리로 뛰어난 성능
- **🛡️ 안정성**: pexpect를 활용한 안정적인 GDB 프로세스 관리
- **🔍 풍부한 기능**: 기존 GDB MCP의 모든 기능을 완전히 구현

## 📋 요구사항

### 시스템 요구사항
- Python 3.8+ 
- Linux, macOS, Windows 지원
- 최소 500MB 디스크 공간
- 인터넷 연결 (패키지 설치용)

### 필수 패키지
**ARM 크로스 컴파일 환경의 경우:**
- `gdb-multiarch` - **ARM 디버깅을 위해 필수**
- `gcc-arm-none-eabi` - ARM GCC 툴체인
- Python 패키지: `fastmcp`, `pexpect`, `psutil`

**일반 환경:**
- `gdb` - 시스템 기본 GDB
- Python 패키지: `fastmcp`, `pexpect`, `psutil`

### ARM 디버깅 환경 설정

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y gdb-multiarch gcc-arm-none-eabi
```

**macOS:**
```bash
brew install gdb arm-none-eabi-gdb
```

**Windows:**
- [ARM GNU Toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads) 다운로드 및 설치

## 🛠️ 설치

### 자동 설치 (권장)

```bash
cd sungdb-mcp
./install.sh
```

### 수동 설치

```bash
cd sungdb-mcp

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 패키지 설치
pip install -e .
```

## 🚀 사용법

### 1. 서버 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
python sungdb_mcp.py
# 또는
sungdb-mcp
```

### 2. Cursor에서 설정

**Cursor의 설정 파일에 다음을 추가합니다:**

#### Windows/Linux: `~/.cursor/config.json`
#### macOS: `~/Library/Application Support/Cursor/config.json`

```json
{
  "mcpServers": {
    "sungdb": {
      "command": "python",
      "args": ["/path/to/cortex-m-hello-world/sungdb-mcp/sungdb_mcp.py"],
      "env": {}
    }
  }
}
```

**또는 가상환경을 활용하는 경우:**

```json
{
  "mcpServers": {
    "sungdb": {
      "command": "/path/to/cortex-m-hello-world/sungdb-mcp/venv/bin/python",
      "args": ["/path/to/cortex-m-hello-world/sungdb-mcp/sungdb_mcp.py"],
      "env": {}
    }
  }
}
```

### 3. Cursor에서 설정

**Cursor의 MCP 설정 파일에 추가합니다:**

#### 설정 방법:
1. Cursor에서 `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)를 눌러 명령 팔레트를 엽니다
2. "Preferences: Open User Settings (JSON)"을 검색하여 선택합니다
3. 설정 파일에 다음을 추가합니다:

```json
{
  "mcp": {
    "mcpServers": {
      "sungdb": {
        "command": "/path/to/cortex-m-hello-world/sungdb-mcp/venv/bin/python",
        "args": ["/path/to/cortex-m-hello-world/sungdb-mcp/sungdb_mcp.py"],
        "env": {}
      }
    }
  }
}
```

**또는 시스템 Python 사용:**
```json
{
  "mcp": {
    "mcpServers": {
      "sungdb": {
        "command": "python3",
        "args": ["/path/to/cortex-m-hello-world/sungdb-mcp/sungdb_mcp.py"],
        "env": {
          "PYTHONPATH": "/path/to/cortex-m-hello-world/sungdb-mcp/venv/lib/python3.11/site-packages"
        }
      }
    }
  }
}
```

**Windows 사용자:**
```json
{
  "mcp": {
    "mcpServers": {
      "sungdb": {
        "command": "C:\\path\\to\\cortex-m-hello-world\\sungdb-mcp\\venv\\Scripts\\python.exe",
        "args": ["C:\\path\\to\\cortex-m-hello-world\\sungdb-mcp\\sungdb_mcp.py"],
        "env": {}
      }
    }
  }
}
```

### 4. Claude Desktop에서 설정

**Claude Desktop의 설정 파일에 추가합니다:**

#### Windows: `%APPDATA%/Claude/claude_desktop_config.json`
#### macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
#### Linux: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sungdb": {
      "command": "/path/to/cortex-m-hello-world/sungdb-mcp/venv/bin/python",
      "args": ["/path/to/cortex-m-hello-world/sungdb-mcp/sungdb_mcp.py"],
      "env": {}
    }
  }
}
```

## 🔧 제공하는 도구들

### 🎮 세션 관리
- `gdb_start` - GDB 세션 시작
- `gdb_terminate` - GDB 세션 종료  
- `gdb_list_sessions` - 활성 세션 목록 조회

### 📂 프로그램 로딩
- `gdb_load` - 실행 파일 로드
- `gdb_attach` - 실행 중인 프로세스에 연결
- `gdb_load_core` - 코어 덤프 파일 로드

### ▶️ 실행 제어
- `gdb_continue` - 프로그램 실행 계속
- `gdb_step` - 스텝 실행 (함수 내부로 진입)
- `gdb_next` - 다음 라인으로 이동 (함수 호출 건너뛰기)
- `gdb_finish` - 현재 함수 끝까지 실행

### 🔴 브레이크포인트
- `gdb_set_breakpoint` - 브레이크포인트 설정

### 🔍 정보 조회
- `gdb_backtrace` - 호출 스택 출력
- `gdb_print` - 변수/표현식 값 출력
- `gdb_examine` - 메모리 내용 검사
- `gdb_info_registers` - 레지스터 정보 출력

### 🎯 범용 명령
- `gdb_command` - 임의의 GDB 명령 실행

## 📋 사용 예시

### 기본 디버깅 워크플로우

```python
# 1. GDB 세션 시작
session = await gdb_start(gdb_path="arm-none-eabi-gdb")

# 2. 프로그램 로드
await gdb_load(session_id, "build/cortex-m33-hello-world.elf")

# 3. 브레이크포인트 설정
await gdb_set_breakpoint(session_id, "main")

# 4. 프로그램 실행 시작
await gdb_continue(session_id)

# 5. 변수 값 확인
await gdb_print(session_id, "variable_name")

# 6. 스텝 실행
await gdb_step(session_id)

# 7. 호출 스택 확인
await gdb_backtrace(session_id)

# 8. 세션 종료
await gdb_terminate(session_id)
```

### Cortex-M 디버깅 예시

```python
# ARM Cortex-M 디버깅용 GDB 세션 시작
session = await gdb_start(
    gdb_path="gdb-multiarch", 
    working_dir="/path/to/cortex-m-hello-world"
)

# ELF 파일 로드
await gdb_load(session_id, "build/cortex-m33-hello-world.elf")

# ARM 아키텍처 설정 (Cortex-M33용)
await gdb_command(session_id, "set architecture armv8-m.main")

# Boot Handler 디스어셈블리 확인
await gdb_command(session_id, "disassemble/r 0x10000008")

# main 함수 디스어셈블리 확인
await gdb_command(session_id, "disassemble/r main")

# QEMU에 연결 (원격 디버깅)
await gdb_command(session_id, "target remote localhost:1234")

# 메인 함수에 브레이크포인트 설정
await gdb_set_breakpoint(session_id, "main")

# 실행 시작
await gdb_continue(session_id)

# ARM 레지스터 확인
await gdb_info_registers(session_id)

# 메모리 검사 (스택 포인터 주변)
await gdb_examine(session_id, "$sp", count=8, format="x")
```

## 🧪 실제 테스트 결과

### Boot Handler (Reset_Handler) Instructions:
```asm
0x10000008 <+0>: 4800    ldr    r0, [pc, #0]    @ (0x1000000c <Reset_Handler+4>)
0x1000000a <+2>: 4700    bx     r0
0x1000000c <+4>: 0045    lsls   r5, r0, #1
0x1000000e <+6>: 1000    asrs   r0, r0, #32
```

### main() 함수 Instructions (일부):
```asm
0x10000044 <+0>:  b570    push   {r4, r5, r6, lr}
0x10000046 <+2>:  2204    movs   r2, #4
0x10000048 <+4>:  b082    sub    sp, #8
0x1000004a <+6>:  4b21    ldr    r3, [pc, #132]  @ (0x100000d0 <main+140>)
0x1000004c <+8>:  4610    mov    r0, r2
0x1000004e <+10>: 4619    mov    r1, r3
0x10000050 <+12>: beab    bkpt   0x00ab  ; Semihosting call
0x10000052 <+14>: 4604    mov    r4, r0
...
0x100000cc <+136>: f7ff ffb0  bl     0x10000030 <exit_program>
```

**테스트 성공!** ✅
- ARM Cortex-M33 아키텍처 정상 인식
- Boot Handler와 main 함수의 ARM Thumb instruction 정상 디스어셈블리
- Semihosting breakpoint (bkpt 0x00ab) 정상 확인
- 함수 호출 및 스택 조작 명령어 정상 표시

## 🏗️ 아키텍처

### 핵심 컴포넌트

1. **SungDBMCP**: 메인 MCP 서버 클래스
   - FastMCP 프레임워크 통합
   - 도구 등록 및 관리
   - 세션 라이프사이클 관리

2. **GDBSession**: 개별 GDB 세션 관리
   - pexpect를 통한 GDB 프로세스 제어
   - 비동기 명령 큐잉 시스템
   - 안전한 명령 실행 및 응답 파싱

3. **명령 큐잉 시스템**:
   - asyncio.Queue를 활용한 FIFO 명령 처리
   - 백그라운드 작업으로 연속적인 명령 실행
   - 명령별 결과 Future를 통한 안전한 응답 처리

### 데이터 플로우

```
LLM Request → FastMCP → SungDBMCP → GDBSession → Command Queue → GDB Process
                ↑                                                        ↓
          JSON Response ← Result Future ← Background Task ← GDB Output
```

## 🧪 테스트

### 기본 기능 테스트

```bash
cd sungdb-mcp
source venv/bin/activate
python -m pytest tests/ -v
```

### 수동 테스트

```bash
# 서버 실행
python sungdb_mcp.py

# 다른 터미널에서 테스트 스크립트 실행
python test_manual.py
```

## 🔧 개발자 가이드

### 새로운 도구 추가

```python
# sungdb_mcp.py에서 _setup_tools 메소드에 추가
self.mcp.add_tool("my_new_tool", "새로운 도구 설명")(self.my_new_tool)

# 새로운 메소드 구현
async def my_new_tool(self, session_id: str, param: str) -> Dict[str, Any]:
    if session_id not in self.sessions:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = self.sessions[session_id]
    return await session.execute_command(f"my_gdb_command {param}")
```

### 로깅 설정

```python
import logging
logging.getLogger("sungdb_mcp").setLevel(logging.DEBUG)
```

## 🚨 문제 해결

### 일반적인 문제들

**Q: "pexpect 모듈을 찾을 수 없습니다"**
```bash
pip install pexpect
```

**Q: "GDB를 찾을 수 없습니다"**
```bash
# ARM 크로스 컴파일러 설치
sudo apt install gcc-arm-none-eabi gdb-multiarch

# 또는 gdb_path 파라미터로 경로 지정
await gdb_start(gdb_path="/usr/bin/gdb-multiarch")
```

**Q: "세션이 응답하지 않습니다"**
- GDB 프로세스가 중단되었을 수 있습니다
- 세션을 종료하고 새로 시작해보세요
- 로그를 확인하여 오류 메시지를 확인하세요

**Q: "FastMCP 서버가 시작되지 않습니다"**
```bash
# 의존성 재설치
pip install --upgrade fastmcp

# 포트 충돌 확인
netstat -tlnp | grep :포트번호
```

### 디버깅 모드

```bash
# 디버그 모드로 서버 실행
PYTHONPATH=. python -m logging --level=DEBUG sungdb_mcp.py
```

## 📊 성능 최적화

### 권장 설정

- **동시 세션 수**: 최대 5개 권장
- **명령 타임아웃**: 30초 (기본값)
- **큐 크기**: 무제한 (메모리 허용 범위 내)

### 모니터링

```python
# 세션 상태 모니터링
sessions_info = await gdb_list_sessions()
print(f"활성 세션 수: {sessions_info['count']}")
```

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 피처 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🔗 관련 링크

- [FastMCP 문서](https://github.com/jlowin/fastmcp)
- [GDB 공식 문서](https://sourceware.org/gdb/documentation/)
- [pexpect 문서](https://pexpect.readthedocs.io/)
- [ARM GCC 툴체인](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm)

## 🆚 기존 GDB MCP와의 차이점

| 기능 | 기존 GDB MCP | SungDB MCP |
|------|-------------|------------|
| 안정성 | ⚠️ 불안정 | ✅ 안정적 |
| 명령 큐잉 | ❌ 없음 | ✅ 비동기 큐잉 |
| 세션 관리 | 🔄 기본적 | 🎯 고급 관리 |
| 오류 처리 | ⚠️ 제한적 | ✅ 포괄적 |
| 성능 | 🐌 느림 | ⚡ 빠름 |
| 로깅 | ❌ 제한적 | 📊 상세한 로깅 |

---

**🎉 Happy Debugging with SungDB MCP!** 🎉
