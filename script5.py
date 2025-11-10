# script5.py
import argparse
import os
import re
import json
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from collections import defaultdict
import subprocess
import sys

# --- Валидация (как в script4.py) ---
def validate_package_name(package_name):
    if not package_name or package_name.strip() == "":
        raise ValueError("Имя пакета не может быть пустым")
    return package_name.strip()

def validate_repository(repository):
    if repository.startswith(("http://", "https://")):
        parsed = urlparse(repository)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Некорректный URL репозитория")
    else:
        if not os.path.exists(repository):
            raise ValueError(f"Файл или директория {repository} не существует")
    return repository

def validate_repo_mode(mode):
    valid_modes = ["local", "remote"]
    if mode not in valid_modes:
        raise ValueError(f"Недопустимый режим: {mode}. Доступные режимы: {valid_modes}")
    return mode

def validate_version(version):
    if version != "latest" and not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ValueError("Некорректный формат версии (X.Y.Z или 'latest')")
    return version

def validate_output_file(filename):
    valid_extensions = [".png", ".jpg", ".svg"]
    if not any(filename.endswith(ext) for ext in valid_extensions):
        raise ValueError(f"Имя файла должно иметь расширение: {valid_extensions}")
    return filename

def validate_depth(depth):
    try:
        depth = int(depth)
        if depth <= 0:
            raise ValueError("Максимальная глубина должна быть положительным числом")
        return depth
    except ValueError:
        raise ValueError("Максимальная глубина должна быть числом")

# --- Получение зависимостей ---
def get_package_dependencies(package_name, version, repository):
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
    except Exception as e:
        raise Exception(f"Ошибка получения зависимостей {package_name}: {e}")

def get_latest_version(package_name, repository):
    try:
        base_url = repository.rstrip('/')
        url = f"{base_url}/{package_name}/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data['info']['version']
    except Exception as e:
        raise Exception(f"Ошибка при получении версии {package_name}: {e}")

def load_graph_from_file(file_path):
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

# --- Построение графа ---
def build_graph_from_pypi(package, repository, version, depth):
    graph = defaultdict(list)
    cache = {}
    def get_deps(pkg):
        if pkg in cache:
            return cache[pkg]
        pkg_ver = version if pkg == package else get_latest_version(pkg, repository)
        deps = get_package_dependencies(pkg, pkg_ver, repository)
        cache[pkg] = deps
        return deps
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
            if d not in path:
                stack.append((d, dep + 1, path + [d]))
    return dict(graph)

# --- D2 генерация ---
def generate_d2(graph, output_d2):
    with open(output_d2, 'w', encoding='utf-8') as f:
        f.write("direction: down\n")
        for pkg, deps in graph.items():
            for dep in deps:
                f.write(f'"{pkg}" -> "{dep}"\n')
    print(f"D2 файл сохранён: {output_d2}")

# --- PNG рендер ---
def render_d2_to_png(d2_file, png_file):
    try:
        result = subprocess.run(
            ["d2", d2_file, png_file],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"PNG сохранён: {png_file}")
    except FileNotFoundError:
        raise Exception("D2 не установлен. Установите: https://d2lang.com/tour/install")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Ошибка D2: {e.stderr}")

# --- ASCII дерево ---
def print_ascii_tree(graph, start_pkg, depth_limit):
    def dfs(pkg, prefix="", depth=0):
        if depth >= depth_limit:
            return
        deps = graph.get(pkg, [])
        for i, dep in enumerate(deps):
            last = i == len(deps) - 1
            print(f"{prefix}{'└── ' if last else '├── '}{dep}")
            new_prefix = prefix + ("    " if last else "│   ")
            dfs(dep, new_prefix, depth + 1)
    print(f"ASCII-дерево зависимостей для {start_pkg}:")
    print(start_pkg)
    dfs(start_pkg)

# --- DFS для транзитивных ---
def get_transitive_dependencies(start_pkg, get_deps, max_depth):
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
        except:
            continue
        for dep in deps:
            if dep in path:
                cycle_detected = True
                continue
            dependencies.add(dep)
            stack.append((dep, depth + 1, path + [dep]))
    return dependencies, cycle_detected

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Этап 5: Визуализация графа зависимостей")
    parser.add_argument("--package", required=True, help="Имя пакета")
    parser.add_argument("--repository", required=True, help="URL или путь к файлу")
    parser.add_argument("--repo-mode", default="remote", help="local/remote")
    parser.add_argument("--version", default="latest", help="Версия (X.Y.Z или 'latest')")
    parser.add_argument("--output", default="graph.png", help="Выходной PNG файл")
    parser.add_argument("--depth", default=2, type=int, help="Глубина анализа")
    parser.add_argument("--ascii", action="store_true", help="Вывести ASCII-дерево")
    parser.add_argument("--reverse", action="store_true", help="Обратные зависимости")

    try:
        args = parser.parse_args()
        package = validate_package_name(args.package)
        repository = validate_repository(args.repository)
        repo_mode = validate_repo_mode(args.repo_mode)
        version = validate_version(args.version)
        output = validate_output_file(args.output)
        depth = validate_depth(args.depth)

        # Определение версии
        if version == "latest" and repo_mode == "remote":
            version = get_latest_version(package, repository)

        print("Настраиваемые параметры:")
        print(f"package: {package}")
        print(f"repository: {repository}")
        print(f"repo_mode: {repo_mode}")
        print(f"version: {version}")
        print(f"output: {output}")
        print(f"depth: {depth}")
        print(f"ascii: {args.ascii}")
        print(f"reverse: {args.reverse}")
        print("\n" + "=" * 50)

        # Построение графа
        if repo_mode == "local":
            graph = load_graph_from_file(repository)
            def get_deps(pkg): return graph.get(pkg, [])
        else:
            print(f"Загрузка графа из PyPI для {package}...")
            graph = build_graph_from_pypi(package, repository, version, depth)
            def get_deps(pkg): return graph.get(pkg, [])

        # Обратные зависимости
        if args.reverse:
            reverse_graph = defaultdict(list)
            for p, deps in graph.items():
                for d in deps:
                    reverse_graph[d].append(p)
            graph = dict(reverse_graph)
            print(f"Построен обратный граф для {package}")

        # D2 + PNG
        d2_file = output.replace('.png', '.d2').replace('.jpg', '.d2').replace('.svg', '.d2')
        generate_d2(graph, d2_file)
        render_d2_to_png(d2_file, output)

        # ASCII
        if args.ascii:
            print("\n")
            print_ascii_tree(graph, package, depth)

        # Сравнение с pipdeptree
        print("\n" + "=" * 50)
        print("Сравнение с pipdeptree:")
        try:
            result = subprocess.run(
                ["pipdeptree", "-p", package, "--depth", str(depth)],
                capture_output=True, text=True, check=True
            )
            print(result.stdout)
        except:
            print("pipdeptree не установлен или ошибка. Установите: pip install pipdeptree")

    except Exception as e:
        print(f"Ошибка: {e}")
        return

if __name__ == "__main__":
    main()
