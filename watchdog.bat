@echo off
chcp 65001 >nul
title Мониторинг крашей
color 0C

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     Автоматический мониторинг папки crash-reports      ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Watchdog запущен. Закрой окно для остановки.
echo.

python scripts\crash_watchdog.py
