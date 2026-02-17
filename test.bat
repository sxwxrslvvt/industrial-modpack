@echo off
chcp 65001 >nul
title Тест сборки Minecraft 1.21.1 NeoForge
color 0A

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║    Локальное тестирование Minecraft 1.21.1 NeoForge    ║
echo ╚════════════════════════════════════════════════════════╝
echo.

python scripts\test_local.py

echo.
echo Нажми любую клавишу для выхода...
pause >nul
