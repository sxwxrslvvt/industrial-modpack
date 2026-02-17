@echo off
chcp 65001 >nul
title Загрузка модов
color 0B

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              Загрузка модов для 1.21.1 NeoForge        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

python scripts\download_mods.py

echo.
echo Нажми любую клавишу для выхода...
pause >nul
