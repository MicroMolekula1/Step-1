# script3.py
import argparse
import os
import re
import json
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError

def validate_package_name(package_name):
    """Проверка, что имя пакета не пустое."""
    if not package_name or package_name.strip() == "":
        raise ValueError("Имя пакета не может быть пустым")
    return package_name.strip()

def validate_repository(repository):
    """Проверка URL или пути к файлу."""
    if repository.startswith(("http://", "https://")):
        parsed = urlparse(repository)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Некорректный URL репозитория")
    else:
        if not os.path.exists(repository):
            raise ValueError(f"Файл или директория {repository} не существует")
    return repository

def validate_repo_mode(mode):
    """Проверка режима работы с репозиторием."""
    valid_modes = ["local", "remote"]
    if mode not in valid_modes:
        raise ValueError(f"Недопустимый режим: {mode}. Доступные режимы: {valid_modes}")
    return mode

def validate_version(version):
    """Проверка версии пакета (например, 1.2.3)."""
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError("Некорректный формат версии пакета (ожидается X.Y.Z)")
    return version

def validate_output_file(filename):
    """Проверка имени выходного файла."""
    valid_extensions = [".png", ".jpg", ".svg"]
    if not any(filename.endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Имя файла должно иметь расширение: {valid_extensions}")
    return filename

def validate_depth(depth):
    """Проверка максимальной глубины анализа."""
    try:
        depth = int(depth)
        if depth <= 0:
            raise ValueError("Максимальная глубина должна быть положительным числом")
        return depth
    except ValueError:
        raise ValueError("Максимальная глубина должна быть числом")

def get_package_dependencies(package_name, version, repository):
    """ Получает прямые зависимости пакета из PyPI.
    Args:
        package_name (str): Имя пакета
        version (str): Версия пакета
        repository (str): URL репозитория PyPI
    Returns:
        list: Список зависимостей
    """
    try:
        base_url = repository.rstrip('/')
        url = f"{base_url}/{package_name}/{version}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
        info = data.get('info', {})
        requires_dist = info.get('requires_dist', [])
        clean_dependencies = []
        for dep in requires_dist:
            clean_dep = re.split(r'[;<>!=()]', dep)[0].strip()
            if clean_dep and clean_dep not in clean_dependencies:
                clean_dependencies.append(clean_dep)
        return clean_dependencies
    except HTTPError as e:
        raise Exception(f"Ошибка HTTP {e.code}: {e.reason}")
    except URLError as e:
        raise Exception(f"Ошибка URL: {e.reason}")
    except json.JSONDecodeError:
        raise Exception("Ошибка декодирования JSON ответа")
    except KeyError:
        raise Exception("Некорректная структура JSON ответа")

def get_latest_version(package_name, repository):
    """Получает последнюю версию пакета из PyPI."""
    try:
        base_url = repository.rstrip('/')
        url = f"{base_url}/{package_name}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data['info']['version']
    except Exception as e:
        raise Exception(f"Ошибка при получении версии пакета {package_name}: {e}")

def load_graph_from_file(file_path):
    """Загружает граф зависимостей из файла."""
    graph = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line:
                pkg, deps_str = line.split(':', 1)
                pkg = pkg.strip()
                deps = [d.strip() for d in deps_str.split() if d.strip()]
                graph[pkg] = deps
    return graph

def get_transitive_dependencies(start_pkg, get_deps, max_depth):
    """Получает транзитивные зависимости с использованием DFS без рекурсии.
    Returns: set зависимостей, bool cycle_detected
    """
    stack = [(start_pkg, 0, [start_pkg])] # реализация DFS через стек.
    visited = set()
    dependencies = set()
    cycle_detected = False
    sub_graph = {}

    while stack:
        pkg, depth, path = stack.pop()
        if pkg in visited:
            continue
        visited.add(pkg)
        if depth >= max_depth: #  УЧЁТ ГЛУБИНЫ.
            continue
        try:
            deps = get_deps(pkg)
        except Exception as e:
            print(f"Ошибка при получении зависимостей для {pkg}: {e}")
            continue
        for dep in deps:
            if dep in path: # ОБНАРУЖЕНИЕ ЦИКЛА.
                cycle_detected = True
                continue  # ОБРАБОТКА ЦИКЛА, не добавляем в стек, чтобы избежать зацикливания, не идём дальше по циклу, продолжаем собирать остальные зависимости.
            dependencies.add(dep)
            new_path = path + [dep]
            stack.append((dep, depth + 1, new_path)) #  DFS БЕЗ РЕКУРСИИ, добавление в стек.

    return dependencies, cycle_detected

def main():
    parser = argparse.ArgumentParser(description="Инструмент визуализации графа зависимостей")
    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--repository", required=True, help="URL репозитория или путь к файлу")
    parser.add_argument("--repo-mode", default="remote", help="Режим работы с репозиторием (local/remote)")
    parser.add_argument("--version", default="1.0.0", help="Версия пакета (X.Y.Z)")
    parser.add_argument("--output", default="graph.png", help="Имя файла с изображением графа")
    parser.add_argument("--ascii", action="store_true", help="Вывод зависимостей в ASCII")
    parser.add_argument("--depth", default=1, type=int, help="Максимальная глубина анализа зависимостей")

    try:
        args = parser.parse_args()
        package = validate_package_name(args.package)
        repository = validate_repository(args.repository)
        repo_mode = validate_repo_mode(args.repo_mode)
        version = validate_version(args.version)
        output = validate_output_file(args.output)
        depth = validate_depth(args.depth)
        ascii_mode = args.ascii

        params = {
            "package": package,
            "repository": repository,
            "repo_mode": repo_mode,
            "version": version,
            "output": output,
            "ascii_mode": ascii_mode,
            "depth": depth
        }
        print("Настраиваемые параметры:")
        for key, value in params.items():
            print(f"{key}: {value}")
        print("\n" + "=" * 50)

        if repo_mode == "remote":
            cache = {}
            def get_deps(pkg):
                if pkg in cache:
                    return cache[pkg]
                ver = version if pkg == package else get_latest_version(pkg, repository)
                deps = get_package_dependencies(pkg, ver, repository)
                cache[pkg] = deps
                return deps
        else:  # local
            graph = load_graph_from_file(repository)
            def get_deps(pkg):
                return graph.get(pkg, [])

        print(f"Получение транзитивных зависимостей для пакета {package}...")
        trans_deps, cycle = get_transitive_dependencies(package, get_deps, depth)
        if cycle:
            print("Обнаружена циклическая зависимость!")
        if trans_deps:
            print(f"\nТранзитивные зависимости пакета {package}:")
            for i, dep in enumerate(sorted(trans_deps), 1):
                print(f"{i}. {dep}")
        else:
            print(f"\nПакет {package} не имеет транзитивных зависимостей на заданной глубине.")

    except ValueError as e:
        print(f"Ошибка валидации: {e}")
        return
    except Exception as e:
        print(f"Ошибка: {e}")
        return

if __name__ == "__main__":
    main()