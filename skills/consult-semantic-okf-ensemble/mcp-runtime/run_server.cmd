@echo off
setlocal
if defined SEMANTIC_OKF_PYTHON (
  "%SEMANTIC_OKF_PYTHON%" "%~dp0semantic_okf_mcp_server.py"
  exit /b %ERRORLEVEL%
)
python "%~dp0semantic_okf_mcp_server.py"
exit /b %ERRORLEVEL%
