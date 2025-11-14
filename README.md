Анализатор зависимостей Python - Этап 5: Визуализация графа
1. Общее описание
Анализатор зависимостей Python - это инструмент для визуализации и анализа графов зависимостей пакетов Python. На пятом этапе проекта реализована расширенная функциональность для графического представления зависимостей с использованием языка диаграмм D2, генерации PNG-изображений и вывода ASCII-деревьев.

Основное назначение:

Анализ прямых и транзитивных зависимостей пакетов

Визуализация сложных отношений между пакетами

Обнаружение циклических зависимостей

Сравнение результатов со стандартными инструментами экосистемы Python

Ключевые особенности:

Поддержка работы с удаленным репозиторием PyPI и локальными файлами

Генерация высококачественных визуализаций в формате PNG

Гибкая настройка глубины анализа

Поддержка анализа обратных зависимостей

Интеграция с инструментом pipdeptree для верификации результатов

2. Описание всех функций и настроек
Основные функциональные модули
Валидация входных данных
validate_package_name(package_name)

Проверяет корректность имени пакета

Исключает пустые значения и строки, состоящие только из пробелов

Возвращает очищенное имя пакета

validate_repository(repository)

Проверяет валидность URL репозитория PyPI

Проверяет существование локальных файлов и директорий

Поддерживает протоколы HTTP и HTTPS

validate_repo_mode(mode)

Проверяет допустимость режима работы

Поддерживаемые режимы: "local", "remote"

validate_version(version)

Проверяет соответствие формату версии X.Y.Z

Поддерживает специальное значение "latest" для получения последней версии

validate_output_file(filename)

Проверяет допустимые расширения файлов: .png, .jpg, .svg

Гарантирует корректность выходного формата

validate_depth(depth)

Проверяет, что глубина анализа - целое положительное число

Обеспечивает разумные ограничения на глубину рекурсии

Работа с зависимостями
get_package_dependencies(package_name, version, repository)

Извлекает информацию о зависимостях через PyPI API

Очищает названия зависимостей от условий установки и версионных ограничений

Обрабатывает специальные условия (extras, environment markers)

Возвращает список очищенных имен зависимостей

get_latest_version(package_name, repository)

Получает последнюю доступную версию пакета из PyPI

Используется при указании версии "latest"

load_graph_from_file(file_path)

Загружает предварительно сохраненный граф зависимостей из файла

Поддерживает простой текстовый формат: "пакет: зависимость1 зависимость2"

Построение и анализ графа
build_graph_from_pypi(package, repository, version, depth)

Рекурсивно строит граф зависимостей до указанной глубины

Использует кэширование для оптимизации сетевых запросов

Обнаруживает и обрабатывает циклические зависимости

Реализует обход в глубину с отслеживанием пути

get_transitive_dependencies(start_pkg, get_deps, max_depth)

Вычисляет транзитивные зависимости с ограничением по глубине

Обнаруживает циклические зависимости

Возвращает множество всех уникальных зависимостей

Визуализация
generate_d2(graph, output_d2)

Генерирует D2-диаграмму из графа зависимостей

Настраивает направление визуализации (сверху вниз)

Создает файл в формате D2 для последующего редактирования

render_d2_to_png(d2_file, png_file)

Конвертирует D2-диаграмму в PNG-изображение

Использует системную утилиту D2 CLI

Обрабатывает ошибки конвертации

print_ascii_tree(graph, start_pkg, depth_limit)

Выводит ASCII-представление дерева зависимостей

Использует символы псевдографики для наглядности

Ограничивает глубину вывода согласно настройкам

Параметры командной строки
Параметр	Обязательный	По умолчанию	Описание
--package	✅ Да	-	Имя анализируемого пакета
--repository	✅ Да	-	URL PyPI или путь к файлу с зависимостями
--repo-mode	❌ Нет	"remote"	Режим работы: "local" или "remote"
--version	❌ Нет	"latest"	Версия пакета (X.Y.Z или "latest")
--output	❌ Нет	"graph.png"	Имя выходного файла изображения
--depth	❌ Нет	2	Максимальная глубина анализа зависимостей
--ascii	❌ Нет	-	Флаг для вывода ASCII-дерева
--reverse	❌ Нет	-	Флаг для анализа обратных зависимостей
Примеры использования параметров
bash
# Анализ зависимостей Django с визуализацией
python script5.py --package django --repository https://pypi.org/pypi --depth 3 --output django_deps.png --ascii

# Анализ обратных зависимостей Flask
python script5.py --package flask --repository https://pypi.org/pypi --depth 2 --reverse --output flask_reverse.png

# Работа с локальным файлом зависимостей
python script5.py --package myapp --repository dependencies.txt --repo-mode local --depth 1
3. Команды для сборки проекта и запуска тестов
Требования к окружению
Python 3.8 или выше

D2 CLI для генерации изображений

pipdeptree для сравнения результатов (опционально)

Установка зависимостей
bash
# Установка D2 CLI (требуется Go)
go install oss.terrastruct.com/d2@latest

# Установка pipdeptree для сравнения
pip install pipdeptree

# Проверка установки D2
d2 --version
Запуск проекта
bash
# Базовый запуск для анализа пакета requests
python script5.py --package requests --repository https://pypi.org/pypi --depth 2

# Запуск с генерацией ASCII-дерева
python script5.py --package django --repository https://pypi.org/pypi --depth 2 --ascii

# Анализ с обратными зависимостями
python script5.py --package numpy --repository https://pypi.org/pypi --depth 1 --reverse
Тестирование функциональности
bash
# Тест 1: Проверка работы с популярными пакетами
python script5.py --package requests --version 2.25.1 --repository https://pypi.org/pypi --depth 1
python script5.py --package django --version 3.2.1 --repository https://pypi.org/pypi --depth 2
python script5.py --package flask --version 2.0.1 --repository https://pypi.org/pypi --depth 2

# Тест 2: Проверка обработки ошибок
python script5.py --package nonexistent-package --repository https://pypi.org/pypi --depth 1
python script5.py --package requests --repository invalid-url --depth 1

# Тест 3: Проверка граничных условий
python script5.py --package requests --repository https://pypi.org/pypi --depth 0
python script5.py --package requests --repository https://pypi.org/pypi --depth 5











