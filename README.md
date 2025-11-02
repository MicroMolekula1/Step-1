# Анализатор зависимостей - Этап 2

## 1. Общее описание

Проект реализует функционал для сбора информации о прямых зависимостях пакетов Python (pip) для заданной пользователем версии пакета. Основная цель — извлечь данные о зависимостях из метаданных пакета, доступных через публичный URL-адрес репозитория PyPI, без использования сторонних библиотек и менеджеров пакетов.

На данном этапе (Этап 2) программа извлекает и выводит на экран список прямых зависимостей указанного пакета и версии. Код написан на Python и использует стандартные модули для работы с HTTP-запросами и парсингом данных.

Результаты сохраняются в репозиторий с использованием стандартно оформленных коммитов.

## 2. Описание всех функций и настроек

### Основные функции

**`get_package_dependencies(package_name, version, repository)`**

- **Назначение**: Извлекает прямые зависимости пакета из PyPI
- **Аргументы**:
  - `package_name` (str) - имя пакета (например, "requests")
  - `version` (str) - версия пакета в формате X.Y.Z (например, "2.25.1")
  - `repository` (str) - URL репозитория PyPI
- **Возвращает**: Список очищенных имен зависимостей
- **Примечание**: Использует API PyPI (`https://pypi.org/pypi/package_name/version/json`)

### Функции валидации

**`validate_package_name(package_name)`**

- Проверяет, что имя пакета не пустое

**`validate_version(version)`**

- Проверяет формат версии (должен соответствовать X.Y.Z)

**`validate_repository(repository)`**

- Проверяет корректность URL репозитория или существование локального пути

**`validate_output_file(filename)`**

- Проверяет допустимые расширения файлов (.png, .jpg, .svg)

**`validate_depth(depth)`**

- Проверяет, что глубина анализа - положительное число

### Настройки командной строки

- `--package` (обязательный) - имя анализируемого пакета
- `--repository` (обязательный) - URL репозитория или путь к файлу
- `--repo-mode` (по умолчанию: "remote") - режим работы: "local" или "remote"
- `--version` (по умолчанию: "1.0.0") - версия пакета в формате X.Y.Z
- `--output` (по умолчанию: "graph.png") - имя файла для сохранения графа
- `--ascii` (флаг) - вывод зависимостей в ASCII формате
- `--depth` (по умолчанию: 1) - максимальная глубина анализа зависимостей

## 3. Команды для сборки проекта и запуска тестов

### Требования

- Python 3.8 или выше
- Стандартные библиотеки Python: `argparse`, `os`, `re`, `json`, `urllib.request`, `urllib.parse`, `urllib.error`

### Установка и запуск

# Клонирование репозитория
git clone <repository_url>
cd <project_directory>

# Запуск скрипта
python script1.py --package requests --version 2.25.1 --repository https://pypi.org/pypi --repo-mode remote
python script2.py --package pytest --version 6.2.4 --repository https://pypi.org/pypi --repo-mode remote --depth 2
python script2.py --package django --version 3.2.1 --repository https://pypi.org/pypi --repo-mode remote --depth 1
python script2.py --package flask --version 2.0.1 --repository https://pypi.org/pypi --repo-mode remote --depth 2

## 4. Примеры использования.

<img width="1591" height="379" alt="image" src="https://github.com/user-attachments/assets/dbad10bd-3fb2-4c2a-9761-d44a7826bf81" />

<img width="1448" height="232" alt="image" src="https://github.com/user-attachments/assets/4ad405d2-3099-4dcb-bb33-e42efb21b390" />











