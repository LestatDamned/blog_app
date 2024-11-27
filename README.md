# Blog App

Веб-приложение на Django для создания и управления блогами. Проект ориентирован на простоту публикации и управления контентом через удобный интерфейс.

## Функционал
- **CRUD-операции**: Создание, просмотр, редактирование и удаление записей.
- **Классы-представления (CBV)**: Модульный и чистый код.
- **Поддержка медиафайлов**: Управление изображениями и другими файлами.
- **Система шаблонов**: Настраиваемые HTML-шаблоны для отображения страниц.

## Технологии
- **Backend**: Python, Django
- **Frontend**: HTML, CSS
- **База данных**: PostgreSQL

## Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/LestatDamned/blog_app.git
   ```
2. Перейдите в папку проекта:
   ```bash
   cd blog_app
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Выполните миграции:
   ```bash
   python manage.py migrate
   ```
5. Запустите сервер разработки:
   ```bash
   python manage.py runserver
   ```
6. Откройте приложение в браузере: `http://127.0.0.1:8000`.

## Структура проекта
- **`apps/`**: Модули приложения.
- **`templates/`**: HTML-шаблоны для отображения страниц.
- **`static/`**: Статические файлы (CSS, JS, изображения).
- **`media/`**: Папка для загружаемых файлов.
- **`manage.py`**: Утилита командной строки Django.

ссылка на развернутый проект https://emo-zone.ru/

