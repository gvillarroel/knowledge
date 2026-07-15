@echo off
setlocal
if not defined SEMANTIC_OKF_PYTHON (
  echo Semantic OKF publication gate requires SEMANTIC_OKF_PYTHON. 1>&2
  exit /b 86
)
"%SEMANTIC_OKF_PYTHON%" "%~dp0confirmed_output_gate.py" %*
exit /b %ERRORLEVEL%
