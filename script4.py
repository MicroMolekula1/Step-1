# script4.py
import argparse
import os
import re
import json
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from collections import defaultdict


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
    """Получает прямые зависимости пакета из PyPI."""
    try:
        base_url = repository.rstrip('/')
        url = f"{base_url}/{package_name}/{version}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
        info = data.get('info', {})
        requires_dist = info.get('requires_dist', [])
        if requires_dist is None:
            requires_dist = []
        clean_dependencies = []
        for dep in requires_dist:
            clean_dep = re.split(r'[;<>!=()]', dep)[0].strip()
            if clean_dep and clean_dep not in clean_dependencies:
                clean_dependencies.append(clean_dep)
        return clean_dependencies
    except HTTPError as e:
        raise Exception(f"Ошибка HTTP {e.code}: {e.reason}")
    except Exception as e:
        raise Exception(f"Ошибка получения зависимостей {package_name}: {e}")


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


def build_graph_from_pypi(package, repository, version, depth):
    """Строит граф зависимостей из PyPI (прямые + транзитивные до глубины)."""
    graph = defaultdict(list)
    cache = {}

    def get_deps(pkg):
        if pkg in cache:
            return cache[pkg]
        pkg_ver = version if pkg == package else get_latest_version(pkg, repository)
        deps = get_package_dependencies(pkg, pkg_ver, repository)
        cache[pkg] = deps
        return deps

    # DFS для построения графа (используем тот же алгоритм)
    stack = [(package, 0, [package])]
    visited = set()

    while stack:
        pkg, dep, path = stack.pop()
        if pkg in visited:
            continue
        visited.add(pkg)
        if dep >= depth:
            continue
        deps = get_deps(pkg)
        graph[pkg] = deps
        for d in deps:
            if d not in path:  # Избежать циклов в построении
                stack.append((d, dep + 1, path + [d]))

    return dict(graph)


def build_reverse_graph(graph):
    """Строит обратный граф."""
    reverse_graph = defaultdict(list)
    for pkg, deps in graph.items():
        for dep in deps:
            reverse_graph[dep].append(pkg)
    return dict(reverse_graph)


def get_transitive_dependencies(start_pkg, get_deps, max_depth):
    """DFS без рекурсии для транзитивных/обратных зависимостей."""
    stack = [(start_pkg, 0, [start_pkg])]
    visited = set()
    dependencies = set()
    cycle_detected = False

    while stack:
        pkg, depth, path = stack.pop()
        if pkg in visited:
            continue
        visited.add(pkg)
        if depth >= max_depth:
            continue
        try:
            deps = get_deps(pkg)
        except Exception as e:
            print(f"Ошибка при получении зависимостей для {pkg}: {e}")
            continue
        for dep in deps:
            if dep in path:
                cycle_detected = True
                continue
            dependencies.add(dep)
            new_path = path + [dep]
            stack.append((dep, depth + 1, new_path))

    return dependencies, cycle_detected


def main():
    parser = argparse.ArgumentParser(description="Этап 4: Обратные зависимости (local/remote)")
    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--repository", required=True, help="URL репозитория или путь к файлу")
    parser.add_argument("--repo-mode", default="remote", help="Режим работы (local/remote)")
    parser.add_argument("--version", default="latest", help="Версия пакета (X.Y.Z или 'latest')")
    parser.add_argument("--output", default="graph.png", help="Имя файла с изображением графа")
    parser.add_argument("--ascii", action="store_true", help="Вывод зависимостей в ASCII")
    parser.add_argument("--depth", default=2, type=int, help="Максимальная глубина анализа")
    parser.add_argument("--reverse", action="store_true", help="Включить режим обратных зависимостей")

    try:
        args = parser.parse_args()
        package = validate_package_name(args.package)
        repository = validate_repository(args.repository)
        repo_mode = validate_repo_mode(args.repo_mode)
        output = validate_output_file(args.output)
        depth = validate_depth(args.depth)
        ascii_mode = args.ascii
        reverse_mode = args.reverse

        # Версия
        if args.version == "latest":
            if repo_mode == "remote":
                version = get_latest_version(package, repository)
            else:
                version = "1.0.0"  # Для local
        else:
            version = validate_version(args.version)

        params = {
            "package": package,
            "repository": repository,
            "repo_mode": repo_mode,
            "version": version,
            "output": output,
            "ascii_mode": ascii_mode,
            "depth": depth,
            "reverse_mode": reverse_mode
        }
        print("Настраиваемые параметры:")
        for key, value in params.items():
            print(f"{key}: {value}")
        print("\n" + "=" * 50)

        if repo_mode == "local":
            graph = load_graph_from_file(repository)
            if not graph:
                raise Exception("Граф зависимостей не существует или пустой")
            if package not in graph and not reverse_mode:
                raise Exception(f"Пакет {package} не найден в графе")

            def get_deps(pkg):
                return graph.get(pkg, [])
        else:  # remote
            print(f"Построение графа из PyPI для {package}...")
            graph = build_graph_from_pypi(package, repository, version, depth)
            if not graph:
                raise Exception(f"Не удалось построить граф для {package}")

            def get_deps(pkg):
                return graph.get(pkg, [])

        # Для reverse — строим обратный граф
        if reverse_mode:
            reverse_graph = build_reverse_graph(graph)

            def get_deps_reverse(pkg):
                return reverse_graph.get(pkg, [])

            print(f"Получение обратных зависимостей от пакета {package}...")
            rev_deps, cycle = get_transitive_dependencies(package, get_deps_reverse, depth)
            prefix = "Обратные"
            if cycle:
                print("Обнаружена циклическая зависимость!")
            if rev_deps:
                print(f"\n{prefix} зависимости от {package}:")
                for i, dep in enumerate(sorted(rev_deps), 1):
                    print(f"{i}. {dep}")
            else:
                raise Exception(f"От пакета {package} никто не зависит на заданной глубине")
        else:
            print(f"Получение транзитивных зависимостей для пакета {package}...")
            trans_deps, cycle = get_transitive_dependencies(package, get_deps, depth)
            prefix = "Транзитивные"
            if cycle:
                print("Обнаружена циклическая зависимость!")
            if trans_deps:
                print(f"\n{prefix} зависимости пакета {package}:")
                for i, dep in enumerate(sorted(trans_deps), 1):
                    print(f"{i}. {dep}")
            else:
                raise Exception(f"Пакет {package} не имеет зависимостей на заданной глубине")

    except ValueError as e:
        print(f"Ошибка валидации: {e}")
        return
    except Exception as e:
        print(f"Ошибка: {e}")
        return


if __name__ == "__main__":
    main()
