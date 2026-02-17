#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локальное тестирование сборки Minecraft 1.21.1 NeoForge на Windows
"""
import subprocess
import os
import sys
import shutil
import time

MC_VERSION = "1.21.1"
MODLOADER = "neoforge"
TEST_DIR = "test_instance"
HEADLESSMC_JAR = r"C:\Tools\HeadlessMC\headlessmc-launcher.jar"

def setup_test_instance():
    """Создаёт тестовый инстанс"""
    print("=" * 60)
    print("=== Подготовка тестового инстанса ===")
    print(f"Версия: Minecraft {MC_VERSION} {MODLOADER.upper()}")
    print("=" * 60)
    print()
    
    # Создаём папки
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(f"{TEST_DIR}\\mods", exist_ok=True)
    
    # Очищаем старые моды
    print("Очистка старых модов...")
    for file in os.listdir(f"{TEST_DIR}\\mods"):
        os.remove(f"{TEST_DIR}\\mods\\{file}")
    
    # Копируем моды
    print("\nКопирование модов...")
    mod_count = 0
    if os.path.exists("mods"):
        for file in os.listdir("mods"):
            if file.endswith('.jar'):
                shutil.copy(f"mods\\{file}", f"{TEST_DIR}\\mods\\{file}")
                print(f"  ✓ {file}")
                mod_count += 1
    
    print(f"\nВсего модов: {mod_count}")
    
    # Копируем конфиги
    if os.path.exists("config"):
        print("\nКопирование конфигов...")
        if os.path.exists(f"{TEST_DIR}\\config"):
            shutil.rmtree(f"{TEST_DIR}\\config")
        shutil.copytree("config", f"{TEST_DIR}\\config")
        print("  ✓ Конфиги скопированы")
    
    # Копируем KubeJS скрипты
    if os.path.exists("kubejs"):
        print("\nКопирование KubeJS скриптов...")
        if os.path.exists(f"{TEST_DIR}\\kubejs"):
            shutil.rmtree(f"{TEST_DIR}\\kubejs")
        shutil.copytree("kubejs", f"{TEST_DIR}\\kubejs")
        print("  ✓ KubeJS скрипты скопированы")
    
    print()

def run_headless_test():
    """Запускает Minecraft через HeadlessMC"""
    print("=" * 60)
    print(f"=== Тестирование Minecraft {MC_VERSION} {MODLOADER.upper()} ===")
    print("=" * 60)
    print()
    
    if not os.path.exists(HEADLESSMC_JAR):
        print(f"✗ ОШИБКА: HeadlessMC не найден: {HEADLESSMC_JAR}")
        print("Скачай с https://github.com/3arthqu4ke/headlessmc/releases")
        print("\nАльтернатива: запуск через обычный лаунчер")
        return False
    
    cmd = [
        "java",
        "-Xmx4G",
        "-Xms2G",
        "-jar", HEADLESSMC_JAR,
        "--command", f"launch {MC_VERSION} {MODLOADER}",
        "--lwjgl", "headless",
        "--timeout", "180"
    ]
    
    print("Запускаю Minecraft...")
    print(f"Команда: {' '.join(cmd)}")
    print("\nЭто может занять 2-3 минуты...\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=TEST_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Ждём завершения с таймаутом 4 минуты
        try:
            stdout, stderr = process.communicate(timeout=240)
            
            print("--- Вывод Minecraft (последние 2000 символов) ---")
            print(stdout[-2000:])
            
            if stderr:
                print("\n--- Ошибки ---")
                print(stderr[-2000:])
            
            if process.returncode != 0:
                print(f"\n⚠ Minecraft завершился с кодом {process.returncode}")
                return False
            
            print("\n✓ Minecraft 1.21.1 NeoForge загрузился успешно!")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            print("\n⚠ ТАЙМАУТ: Тест завис (возможно, зависли моды)")
            print("Попробуй увеличить таймаут или проверь логи")
            return False
            
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        return False

def check_crashes():
    """Проверяет наличие крашей"""
    crash_dir = f"{TEST_DIR}\\crash-reports"
    
    if not os.path.exists(crash_dir):
        return True
    
    crashes = os.listdir(crash_dir)
    if crashes:
        print(f"\n⚠ КРАШ ОБНАРУЖЕН: найдено {len(crashes)} краш-репортов")
        for crash in crashes:
            print(f"  - {crash}")
        
        print("\nЗапусти для анализа:")
        print("  python scripts\\analyze_crash_local.py")
        return False
    
    return True

def check_mods_compatibility():
    """Проверяет базовую совместимость модов"""
    print("\n--- Проверка совместимости модов ---")
    
    mods_dir = "mods"
    if not os.path.exists(mods_dir):
        print("⚠ Папка mods не найдена")
        return
    
    mods = [f for f in os.listdir(mods_dir) if f.endswith('.jar')]
    
    # Проверяем наличие обязательных модов для 1.21.1
    required_mods = {
        "kubejs": False,
        "architectury": False,  # Часто требуется для Create и других
        "jei": False
    }
    
    for mod in mods:
        mod_lower = mod.lower()
        for required in required_mods.keys():
            if required in mod_lower:
                required_mods[required] = True
    
    print("\nОбязательные моды:")
    for mod, present in required_mods.items():
        status = "✓" if present else "✗"
        print(f"  {status} {mod}")
    
    print()

def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║  Локальное тестирование сборки Minecraft 1.21.1 NeoForge  ║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Проверка модов
    check_mods_compatibility()
    
    # Подготовка
    setup_test_instance()
    
    # Тестирование
    success = run_headless_test()
    
    # Проверка крашей
    no_crashes = check_crashes()
    
    print("\n" + "=" * 60)
    if success and no_crashes:
        print("✓✓✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ ✓✓✓")
        print("Сборка совместима с Minecraft 1.21.1 NeoForge!")
    else:
        print("✗✗✗ ТЕСТЫ ПРОВАЛЕНЫ ✗✗✗")
        if not success:
            print("Minecraft не запустился или завис")
        if not no_crashes:
            print("Обнаружены краши - запусти analyze_crash_local.py")
    print("=" * 60)
    print()
    
    return 0 if (success and no_crashes) else 1

if __name__ == "__main__":
    sys.exit(main())
