@echo off
chcp 65001 >nul
title Анализ крашей через Ollama
color 0E

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║         Анализ крашей Minecraft 1.21.1 NeoForge        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

python scripts\analyze_crash_local.py

echo.
echo Нажми любую клавишу для выхода...
pause >nul
