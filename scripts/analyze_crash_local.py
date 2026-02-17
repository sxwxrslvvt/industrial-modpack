#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ крашей Minecraft 1.21.1 NeoForge через локальную Ollama
"""
import requests
import json
import glob
import os

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"  # Или "qwen2.5:7b" для более точного анализа
CRASH_DIR = "crash-reports"

def check_ollama_running():
    """Проверяет, запущена ли Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def analyze_with_ollama(crash_text):
    """Отправляет краш в Ollama"""
    if not check_ollama_running():
        print("✗ ОШИБКА: Ollama не запущена!")
        print("Запустите Ollama из меню Пуск или через: ollama serve")
        return None
    
    prompt = f"""Ты эксперт по Minecraft модам, специализируешься на версии 1.21.1 и модлоадере NeoForge.

Проанализируй этот краш-репорт и определи:

1. **Виновник**: Какой мод вызвал краш (название и версия)
2. **Причина**: Почему это произошло (конфликт модов, несовместимость с 1.21.1, ошибка в коде)
3. **Решение**: Конкретные шаги для исправления
4. **Совместимость**: Есть ли известные проблемы этого мода с NeoForge 1.21.1

Краш-репорт:
{crash_text[:4000]}

Дай ответ на русском языке в структурированном формате."""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9
        }
    }
    
    print(f"Анализирую через Ollama ({MODEL})...")
    print("Это может занять 30-90 секунд...\n")
    
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=180)
        
        if response.status_code != 200:
            print(f"✗ Ошибка Ollama: {response.status_code}")
            return None
        
        result = response.json()
        return result.get("response", "")
        
    except requests.Timeout:
        print("✗ ТАЙМАУТ: Ollama не ответила за 3 минуты")
        print("Попробуй более лёгкую модель: ollama pull llama3.2:3b")
        return None
    except Exception as e:
        print(f"✗ ОШИБКА: {e}")
        return None

def main():
    print("=" * 60)
    print("=== Локальный AI-анализ крашей (1.21.1 NeoForge) ===")
    print("=" * 60)
    print()
    
    # Ищем краши
    if not os.path.exists(CRASH_DIR):
        print("✓ Папка crash-reports не найдена (нет крашей)")
        return 0
    
    crashes = glob.glob(f"{CRASH_DIR}\\*.txt")
    
    if not crashes:
        print("✓ Крашей не обнаружено!")
        return 0
    
    # Берём последний
    latest_crash = max(crashes, key=os.path.getctime)
    print(f"Найден краш: {latest_crash}\n")
    
    # Читаем
    with open(latest_crash, 'r', encoding='utf-8', errors='ignore') as f:
        crash_content = f.read()
    
    # Показываем превью
    print("--- Превью краш-репорта ---")
    print(crash_content[:400])
    print("...\n")
    
    # Проверяем версию в краше
    if "1.21.1" in crash_content:
        print("✓ Подтверждена версия: Minecraft 1.21.1")
    if "neoforge" in crash_content.lower():
        print("✓ Подтверждён модлоадер: NeoForge")
    print()
    
    # Анализируем
    analysis = analyze_with_ollama(crash_content)
    
    if analysis:
        print("=" * 60)
        print("=== AI Анализ (Локальный - Ollama) ===")
        print("=" * 60)
        print(analysis)
        print("=" * 60)
        
        # Сохраняем
        analysis_file = latest_crash.replace('.txt', '_analysis_local.txt')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write("=== Локальный AI-анализ через Ollama ===\n")
            f.write(f"Модель: {MODEL}\n")
            f.write(f"Версия игры: Minecraft 1.21.1 NeoForge\n\n")
            f.write(analysis)
        
        print(f"\n✓ Анализ сохранён: {analysis_file}")
    
    return 0

if __name__ == "__main__":
    main()
