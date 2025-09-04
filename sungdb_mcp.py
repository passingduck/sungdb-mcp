#!/usr/bin/env python3
"""
SungDB MCP Server - A FastMCP-based GDB debugging server
Provides comprehensive GDB debugging capabilities with session management
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import tempfile
import time
import uuid
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pexpect
import psutil
from fastmcp import FastMCP
from fastmcp.tools import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GDBSession:
    """Manages a single GDB debugging session"""
    
    def __init__(self, session_id: str, gdb_path: str = "gdb", working_dir: Optional[str] = None):
        self.session_id = session_id
        self.gdb_path = gdb_path
        self.working_dir = working_dir or os.getcwd()
        self.process: Optional[pexpect.spawn] = None
        self.is_active = False
        self.command_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        
    async def start(self) -> Dict[str, Any]:
        """Start the GDB session"""
        try:
            # Start GDB with machine interface
            cmd = [self.gdb_path, "--interpreter=mi3", "--quiet"]
            
            self.process = pexpect.spawn(
                ' '.join(cmd),
                cwd=self.working_dir,
                encoding='utf-8',
                timeout=30
            )
            
            # Wait for GDB to start
            self.process.expect(r'\(gdb\)', timeout=10)
            self.is_active = True
            
            # Start command processing task
            self._processing_task = asyncio.create_task(self._process_commands())
            
            logger.info(f"GDB session {self.session_id} started successfully")
            return {
                "status": "success",
                "session_id": self.session_id,
                "message": f"GDB session started with PID {self.process.pid}",
                "gdb_path": self.gdb_path,
                "working_dir": self.working_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to start GDB session {self.session_id}: {e}")
            self.is_active = False
            return {
                "status": "error",
                "session_id": self.session_id,
                "error": str(e)
            }
    
    async def _process_commands(self):
        """Background task to process queued commands"""
        while self.is_active and self.process and self.process.isalive():
            try:
                # Get command from queue with timeout
                command, result_future = await asyncio.wait_for(
                    self.command_queue.get(), timeout=1.0
                )
                
                # Execute the command
                result = await self._execute_command_internal(command)
                result_future.set_result(result)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing command in session {self.session_id}: {e}")
                if 'result_future' in locals():
                    result_future.set_exception(e)
    
    async def _execute_command_internal(self, command: str) -> Dict[str, Any]:
        """Execute a GDB command and return the result"""
        if not self.is_active or not self.process or not self.process.isalive():
            return {
                "status": "error",
                "error": "GDB session is not active"
            }
        
        try:
            # Send command to GDB
            self.process.sendline(command)
            
            # Wait for response
            output_lines = []
            
            while True:
                try:
                    index = self.process.expect([
                        r'\(gdb\)',  # Normal prompt
                        r'--Type <return> to continue.*--',  # Pager
                        pexpect.TIMEOUT,
                        pexpect.EOF
                    ], timeout=5)
                    
                    if index == 0:  # Normal prompt
                        output_lines.append(self.process.before)
                        break
                    elif index == 1:  # Pager
                        self.process.send('\n')  # Continue paging
                        output_lines.append(self.process.before)
                    elif index == 2:  # Timeout
                        output_lines.append(self.process.before)
                        break
                    else:  # EOF
                        self.is_active = False
                        break
                        
                except pexpect.TIMEOUT:
                    output_lines.append(self.process.before)
                    break
            
            # Join all output
            full_output = '\n'.join(filter(None, output_lines))
            
            return {
                "status": "success",
                "command": command,
                "output": full_output.strip(),
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Error executing command '{command}' in session {self.session_id}: {e}")
            return {
                "status": "error",
                "command": command,
                "error": str(e),
                "session_id": self.session_id
            }
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Queue a command for execution"""
        if not self.is_active:
            return {
                "status": "error",
                "error": "GDB session is not active"
            }
        
        # Create a future for the result
        result_future = asyncio.Future()
        
        # Queue the command
        await self.command_queue.put((command, result_future))
        
        # Wait for the result
        try:
            result = await asyncio.wait_for(result_future, timeout=30)
            return result
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "error": "Command execution timed out",
                "command": command
            }
    
    async def terminate(self) -> Dict[str, Any]:
        """Terminate the GDB session"""
        try:
            self.is_active = False
            
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            
            if self.process and self.process.isalive():
                # Try graceful shutdown first
                try:
                    self.process.sendline("quit")
                    self.process.expect(pexpect.EOF, timeout=5)
                except:
                    # Force kill if graceful shutdown fails
                    self.process.terminate(force=True)
            
            logger.info(f"GDB session {self.session_id} terminated")
            return {
                "status": "success",
                "session_id": self.session_id,
                "message": "GDB session terminated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error terminating GDB session {self.session_id}: {e}")
            return {
                "status": "error",
                "session_id": self.session_id,
                "error": str(e)
            }

# Global sessions dictionary to maintain state across tool calls
SESSIONS: Dict[str, GDBSession] = {}

# Create FastMCP server instance
mcp = FastMCP("SungDB MCP Server")

# Session management tools
async def gdb_start(gdb_path: str = "gdb", working_dir: Optional[str] = None) -> Dict[str, Any]:
    """Start a new GDB session"""
    session_id = str(uuid.uuid4())
    session = GDBSession(session_id, gdb_path, working_dir)
    
    result = await session.start()
    
    if result["status"] == "success":
        SESSIONS[session_id] = session
    
    return result

async def gdb_terminate(session_id: str) -> Dict[str, Any]:
    """Terminate a GDB session"""
    if session_id not in SESSIONS:
        return {
            "status": "error",
            "error": f"Session {session_id} not found"
        }
    
    session = SESSIONS[session_id]
    result = await session.terminate()
    
    if result["status"] == "success":
        del SESSIONS[session_id]
    
    return result

async def gdb_list_sessions(dummy: str = "") -> Dict[str, Any]:
    """List all active GDB sessions"""
    active_sessions = []
    
    for session_id, session in SESSIONS.items():
        active_sessions.append({
            "session_id": session_id,
            "gdb_path": session.gdb_path,
            "working_dir": session.working_dir,
            "is_active": session.is_active,
            "pid": session.process.pid if session.process and session.process.isalive() else None
        })
    
    return {
        "status": "success",
        "sessions": active_sessions,
        "count": len(active_sessions)
    }

# Program loading and attachment
async def gdb_load(session_id: str, program: str, arguments: Optional[List[str]] = None) -> Dict[str, Any]:
    """Load a program into GDB"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    # Load the program
    load_result = await session.execute_command(f"file {program}")
    
    if arguments:
        args_str = " ".join(arguments)
        args_result = await session.execute_command(f"set args {args_str}")
        load_result["arguments_result"] = args_result
    
    return load_result

async def gdb_attach(session_id: str, pid: int) -> Dict[str, Any]:
    """Attach to a running process"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    return await session.execute_command(f"attach {pid}")

async def gdb_load_core(session_id: str, program: str, core_path: str) -> Dict[str, Any]:
    """Load a core dump file"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    # Load program first
    load_result = await session.execute_command(f"file {program}")
    
    # Load core dump
    core_result = await session.execute_command(f"core {core_path}")
    
    return {
        "status": "success",
        "file_result": load_result,
        "core_result": core_result
    }

# Execution control
async def gdb_continue(session_id: str) -> Dict[str, Any]:
    """Continue program execution"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    return await session.execute_command("continue")

async def gdb_step(session_id: str, instructions: bool = False) -> Dict[str, Any]:
    """Step program execution"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    command = "stepi" if instructions else "step"
    return await session.execute_command(command)

async def gdb_next(session_id: str, instructions: bool = False) -> Dict[str, Any]:
    """Step over function calls"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    command = "nexti" if instructions else "next"
    return await session.execute_command(command)

async def gdb_finish(session_id: str) -> Dict[str, Any]:
    """Execute until the current function returns"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    return await session.execute_command("finish")

# Breakpoints
async def gdb_set_breakpoint(session_id: str, location: str, condition: Optional[str] = None) -> Dict[str, Any]:
    """Set a breakpoint"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    if condition:
        command = f"break {location} if {condition}"
    else:
        command = f"break {location}"
    
    return await session.execute_command(command)

# Information and debugging
async def gdb_backtrace(session_id: str, full: bool = False, limit: Optional[int] = None) -> Dict[str, Any]:
    """Show call stack"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    if full:
        command = "bt full"
    else:
        command = "bt"
    
    if limit:
        command += f" {limit}"
    
    return await session.execute_command(command)

async def gdb_print(session_id: str, expression: str) -> Dict[str, Any]:
    """Print value of expression"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    return await session.execute_command(f"print {expression}")

async def gdb_examine(session_id: str, expression: str, count: Optional[int] = None, format: Optional[str] = None) -> Dict[str, Any]:
    """Examine memory"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    command = "x"
    if count and format:
        command += f"/{count}{format}"
    elif count:
        command += f"/{count}"
    elif format:
        command += f"/{format}"
    
    command += f" {expression}"
    
    return await session.execute_command(command)

async def gdb_info_registers(session_id: str, register: Optional[str] = None) -> Dict[str, Any]:
    """Display registers"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    
    if register:
        command = f"info registers {register}"
    else:
        command = "info registers"
    
    return await session.execute_command(command)

# Generic command execution
async def gdb_command(session_id: str, command: str) -> Dict[str, Any]:
    """Execute a GDB command"""
    if session_id not in SESSIONS:
        return {"status": "error", "error": f"Session {session_id} not found"}
    
    session = SESSIONS[session_id]
    return await session.execute_command(command)

# Register all tools
mcp.add_tool(Tool.from_function(gdb_start, name="gdb_start", description="Start a new GDB session"))
mcp.add_tool(Tool.from_function(gdb_terminate, name="gdb_terminate", description="Terminate a GDB session"))
mcp.add_tool(Tool.from_function(gdb_list_sessions, name="gdb_list_sessions", description="List all active GDB sessions"))

mcp.add_tool(Tool.from_function(gdb_load, name="gdb_load", description="Load a program into GDB"))
mcp.add_tool(Tool.from_function(gdb_attach, name="gdb_attach", description="Attach to a running process"))
mcp.add_tool(Tool.from_function(gdb_load_core, name="gdb_load_core", description="Load a core dump file"))

mcp.add_tool(Tool.from_function(gdb_continue, name="gdb_continue", description="Continue program execution"))
mcp.add_tool(Tool.from_function(gdb_step, name="gdb_step", description="Step program execution"))
mcp.add_tool(Tool.from_function(gdb_next, name="gdb_next", description="Step over function calls"))
mcp.add_tool(Tool.from_function(gdb_finish, name="gdb_finish", description="Execute until the current function returns"))

mcp.add_tool(Tool.from_function(gdb_set_breakpoint, name="gdb_set_breakpoint", description="Set a breakpoint"))

mcp.add_tool(Tool.from_function(gdb_backtrace, name="gdb_backtrace", description="Show call stack"))
mcp.add_tool(Tool.from_function(gdb_print, name="gdb_print", description="Print value of expression"))
mcp.add_tool(Tool.from_function(gdb_examine, name="gdb_examine", description="Examine memory"))
mcp.add_tool(Tool.from_function(gdb_info_registers, name="gdb_info_registers", description="Display registers"))

mcp.add_tool(Tool.from_function(gdb_command, name="gdb_command", description="Execute a GDB command"))

async def cleanup():
    """Clean up all sessions"""
    logger.info("Cleaning up all GDB sessions...")
    for session_id in list(SESSIONS.keys()):
        try:
            await gdb_terminate(session_id)
        except Exception as e:
            logger.error(f"Error terminating session {session_id}: {e}")

def main():
    """Main entry point"""
    logger.info("Starting SungDB MCP Server...")
    logger.info("Press Ctrl+C to stop the server")
    
    # Set up signal handlers - use the default behavior for STDIO mode
    import signal
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # Run cleanup synchronously
        import asyncio
        try:
            # Try to clean up sessions if possible
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(cleanup())
            loop.close()
        except Exception as e:
            logger.warning(f"Could not clean up sessions: {e}")
        
        logger.info("SungDB MCP Server shutdown complete")
        exit(0)
    
    # Install signal handlers
    signal.signal(signal.SIGINT, signal_handler) 
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the server directly - FastMCP handles STDIO transport
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
        # Run cleanup
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(cleanup())
            loop.close()
        except Exception as e:
            logger.warning(f"Could not clean up sessions: {e}")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("SungDB MCP Server shutdown complete")


if __name__ == "__main__":
    main()
