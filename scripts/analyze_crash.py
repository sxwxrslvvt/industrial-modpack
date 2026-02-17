#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализирует краш-репорты через Perplexity API
"""
import os
import sys
import glob
import requests
import json

PERPLEXITY_API = "https://api.perplexity.ai/chat/completions"

def get_latest_crash():
    """Находит последний краш-репорт"""
    crash_dir = "crash-reports"
    
    if not os.path.exists(crash_dir):
        return None
    
    crashes = glob.glob(f"{crash_dir}/*.txt")
    if not crashes:
        return None
    
    return max(crashes, key=os.path.getctime)

def analyze_crash_with_perplexity(crash_content):
    """Отправляет краш в Perplexity API"""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("⚠ ПРЕДУПРЕЖДЕНИЕ: PERPLEXITY_API_KEY не установлен")
        print("Установите переменную окружения или добавьте в GitHub Secrets")
        return None
    
    # Берём первые 8000 символов
    crash_sample = crash_content[:8000]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",  # Или "sonar-pro" для более глубокого анализа
        "messages": [
            {
                "role": "system",
                "content": "Ты эксперт по Minecraft модам и NeoForge. Анализируй краш-репорты на русском языке и давай конкретные рекомендации по исправлению."
            },
            {
                "role": "user",
                "content": f"""Проанализируй этот краш-репорт Minecraft 1.21.1 NeoForge и определи:

1. Какой мод вызвал краш
2. Почему это произошло (конфликт модов, несовместимость версий, ошибка конфига)
3. Конкретные шаги для исправления
4. Есть ли известные решения для этой проблемы

Краш-репорт:
{crash_sample}

Дай ответ в формате:
**Виновник:** [название мода]
**Причина:** [краткое объяснение]
**Решение:** [конкретные шаги]
**Ссылки:** [если есть]"""
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
        "top_p": 0.9,
        "return_citations": True,  # Perplexity вернёт источники
        "search_domain_filter": ["modrinth.com", "curseforge.com", "github.com"],
        "search_recency_filter": "month"  # Искать только свежие решения
    }
    
    print("Отправляю краш в Perplexity для анализа...")
    print("Perplexity ищет решения в интернете...\n")
    
    try:
        response = requests.post(
            PERPLEXITY_API,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"✗ ОШИБКА Perplexity API: {response.status_code}")
            print(f"Ответ: {response.text}")
            return None
        
        result = response.json()
        analysis = result["choices"][0]["message"]["content"]
        
        # Извлекаем цитаты (источники) если есть
        citations = result.get("citations", [])
        
        return {
            "analysis": analysis,
            "citations": citations
        }
        
    except requests.Timeout:
        print("✗ ТАЙМАУТ: Perplexity не ответил за 60 секунд")
        return None
    except Exception as e:
        print(f"✗ ОШИБКА при анализе: {e}")
        return None

def check_logs_for_errors():
    """Проверяет логи на ошибки"""
    logs_dir = "logs"
    latest_log = os.path.join(logs_dir, "latest.log")
    
    if not os.path.exists(latest_log):
        return False
    
    with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if "ERROR" in content or "FATAL" in content:
            print("⚠ В логах найдены ошибки (ERROR/FATAL)")
            return True
    
    return False

def main():
    print("=" * 60)
    print("=== Анализ крашей Minecraft 1.21.1 NeoForge ===")
    print("=" * 60)
    print()
    
    # Проверяем краши
    crash_file = get_latest_crash()
    
    if not crash_file:
        print("✓ Крашей не обнаружено!")
        
        # Проверяем логи
        if check_logs_for_errors():
            print("⚠ Но в логах есть ошибки")
            return 1
        else:
            print("✓ Логи чистые!")
            return 0
    
    # Читаем краш
    print(f"Найден краш: {crash_file}")
    print()
    
    with open(crash_file, 'r', encoding='utf-8', errors='ignore') as f:
        crash_content = f.read()
    
    # Показываем превью
    print("--- Превью краш-репорта ---")
    print(crash_content[:500])
    print("...")
    print()
    
    # AI анализ через Perplexity
    result = analyze_crash_with_perplexity(crash_content)
    
    if result:
        analysis = result["analysis"]
        citations = result["citations"]
        
        print("=" * 60)
        print("=== Perplexity AI Анализ ===")
        print("=" * 60)
        print(analysis)
        print()
        
        # Показываем источники
        if citations:
            print("--- Источники информации ---")
            for i, citation in enumerate(citations, 1):
                print(f"{i}. {citation}")
            print()
        
        print("=" * 60)
        print()
        
        # Сохраняем анализ
        analysis_file = crash_file.replace('.txt', '_analysis.txt')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write("=== Perplexity AI Анализ ===\n\n")
            f.write(analysis)
            f.write("\n\n--- Источники ---\n")
            for i, citation in enumerate(citations, 1):
                f.write(f"{i}. {citation}\n")
        
        print(f"✓ Анализ сохранён: {analysis_file}")
    
    return 1  # Exit code 1 = краш обнаружен

if __name__ == "__main__":
    sys.exit(main())
