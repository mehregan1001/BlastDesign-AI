@echo off
cd /d "%~dp0"
call conda activate mining-ai
jupyter lab
