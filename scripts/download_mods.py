#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматически скачивает моды из modlist/mods.txt
"""
import os
import sys
import urllib.request
import hashlib

MODLIST_FILE = "modlist/mods.txt"
MODS_DIR = "mods"

def download_file(url, destination):
    """Скачивает файл"""
    print(f"Скачиваю: {url}")
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Сохранено: {destination}")
        return True
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def verify_sha256(file_path, expected_hash):
    """Проверяет SHA256 хеш"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

def main():
    # Создаём папку для модов
    os.makedirs(MODS_DIR, exist_ok=True)
    
    # Проверяем наличие файла со списком
    if not os.path.exists(MODLIST_FILE):
        print(f"ОШИБКА: Файл {MODLIST_FILE} не найден!")
        sys.exit(1)
    
    print(f"=== Загрузка модов из {MODLIST_FILE} ===\n")
    
    # Читаем список модов
    with open(MODLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    success_count = 0
    fail_count = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith('#'):
            continue
        
        # Парсим строку
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 2:
            print(f"⚠ Строка {line_num}: неверный формат (нужно: название | URL)")
            continue
        
        name = parts[0]
        url = parts[1]
        expected_hash = parts[2] if len(parts) > 2 else None
        
        # Определяем имя файла
        filename = url.split('/')[-1]
        if not filename.endswith('.jar'):
            filename = f"{name}.jar"
        
        destination = os.path.join(MODS_DIR, filename)
        
        # Проверяем, не скачан ли уже
        if os.path.exists(destination):
            print(f"✓ Уже существует: {filename}")
            
            # Проверяем хеш если указан
            if expected_hash:
                if verify_sha256(destination, expected_hash):
                    print(f"  ✓ SHA256 проверен")
                else:
                    print(f"  ⚠ SHA256 не совпадает! Перезагружаю...")
                    os.remove(destination)
                    if download_file(url, destination):
                        success_count += 1
                    else:
                        fail_count += 1
            continue
        
        # Скачиваем
        if download_file(url, destination):
            success_count += 1
            
            # Проверяем хеш
            if expected_hash:
                if verify_sha256(destination, expected_hash):
                    print(f"  ✓ SHA256 проверен")
                else:
                    print(f"  ⚠ SHA256 не совпадает!")
        else:
            fail_count += 1
        
        print()  # Пустая строка для читабельности
    
    print("=" * 50)
    print(f"✓ Успешно: {success_count}")
    print(f"✗ Ошибок: {fail_count}")
    print("=" * 50)
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
