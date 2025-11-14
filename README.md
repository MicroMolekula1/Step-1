# Этап 5: Визуализация графа зависимостей

## 1. Общее описание

Реализована **функция визуализации графа зависимостей** с использованием языка диаграмм D2 и генерацией PNG изображений. Добавлена возможность **вывода ASCII-дерева** зависимостей в консоль.

- Используется **D2 язык** для описания графов с последующей конвертацией в PNG
- Поддерживается **ограничение глубины** анализа
- Реализовано **ASCII-представление** дерева зависимостей для быстрого просмотра
- Работает **как с удаленным PyPI**, так и с локальными файлами графов
- Интегрировано **сравнение с pipdeptree** для верификации результатов

> **Цель**: получить наглядное графическое представление графа зависимостей пакета

---

## 2. Описание всех функций и настроек

### Параметры командной строки:

| Параметр | Описание |
|----------|-----------|
| `--package` | **Обязательный**. Имя анализируемого пакета |
| `--repository` | **Обязательный**. URL PyPI или путь к файлу с графом |
| `--repo-mode` | Режим работы: "local" или "remote" (по умолчанию: "remote") |
| `--version` | Версия пакета в формате X.Y.Z или "latest" (по умолчанию: "latest") |
| `--output` | Имя файла для сохранения графа (по умолчанию: "graph.png") |
| `--depth` | Максимальная глубина анализа (по умолчанию: 2) |
| `--ascii` | **Флаг**. Вывод зависимостей в виде ASCII-дерева |
| `--reverse` | **Флаг**. Включение режима обратных зависимостей |

### Внутренние функции:

| Функция | Описание |
|---------|-----------|
| `validate_package_name()` | Проверяет корректность имени пакета |
| `validate_repository()` | Проверяет URL репозитория или существование локального файла |
| `validate_version()` | Проверяет формат версии (X.Y.Z или "latest") |
| `validate_output_file()` | Проверяет допустимые расширения файлов (.png, .jpg, .svg) |
| `validate_depth()` | Проверяет, что глубина - положительное число |
| `get_package_dependencies()` | Извлекает зависимости пакета из PyPI API |
| `get_latest_version()` | Получает последнюю версию пакета из PyPI |
| `load_graph_from_file()` | Загружает граф из файла формата `A: B C` |
| `build_graph_from_pypi()` | Строит граф зависимостей из PyPI с ограничением глубины |
| `generate_d2()` | Генерирует D2-диаграмму из графа зависимостей |
| `render_d2_to_png()` | Конвертирует D2-файл в PNG изображение |
| `print_ascii_tree()` | Выводит ASCII-дерево зависимостей в консоль |
| `get_transitive_dependencies()` | Вычисляет транзитивные зависимости (итеративный DFS) |

---

## 3. Описание команд для запуска и тестирования

### Установка зависимостей:

```bash
python script5.py --package requests --repository https://pypi.org/pypi --repo-mode remote --version latest --depth 1 --output requests.png --ascii

python script5.py --package matplotlib --repository https://pypi.org/pypi --repo-mode remote --version latest --depth 2 --output mpl.png

python script5.py --package idna --repository test_graph.txt --repo-mode local --depth 3 --output diagram.png --ascii
```

## 4. Результаты тестирования

<img width="587" height="515" alt="image" src="https://github.com/user-attachments/assets/5d676e83-1381-4ec6-b8a2-b1273c040154" />

<img width="1562" height="334" alt="image" src="https://github.com/user-attachments/assets/b21375b9-596e-4fd9-9d08-5193908017e3" />

<img width="1730" height="580" alt="image" src="https://github.com/user-attachments/assets/3e448231-bc2a-464c-9b42-7556828f3603" />














