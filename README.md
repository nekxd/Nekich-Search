# Nekich Search (Ретро-поиск Google 2014)

Полнофункциональный легковесный поисковик в стиле классического интерфейса **Google 2014 года**, оптимизированный для старых браузеров (Internet Explorer 6, Netscape, Opera и др.) и современных систем.

---

## 🌟 Особенности

- **Ретро-дизайн 2014 года**: Аутентичный чистый внешний вид Google 2014 года.
- **Без `gbar` и без вкладок**: Верхняя панель Google и лишние вкладки удалены.
- **Поиск DuckDuckGo + Wikipedia**: Полноценный поиск по вебу с мгновенными ответами.
- **Иконки сайтов (Favicons)**: Отображение иконки каждого сайта в результатах поиска.
- **5 Ротируемых баннеров с переходами**:
  1. **Inori Aizawa** (`http://faero.top/ad/inori.png`) &rarr; [http://inori.faero.top](http://inori.faero.top)
  2. **LunaStore** (`http://faero.top/ad/ls_rek.png`) &rarr; [http://lunastore.app](http://lunastore.app)
  3. **Renaissance** (`http://faero.top/ad/mrim.jpg`) &rarr; [http://mrim.su](http://mrim.su)
  4. **FaeroFM** (`http://faero.top/ad/faerofm.png`) &rarr; [http://fm.faero.top](http://fm.faero.top)
  5. **faero.top** (`http://faero.top/ad/faero.png`) &rarr; [http://faero.top](http://faero.top)
- **Страницы**:
  - `about.html` (`/about`) — **О компании** (информация о проекте и создателе).
  - `advertising.html` (`/advertising`) — **Реклама** (контакты для размещения рекламы: `nekxd@bk.ru`).
  - `settings.html` (`/settings`) — **Настройки** (возможность отключения показа рекламы через Cookies / LocalStorage).
  - `business.html` (`/business`), `privacy.html` (`/privacy`), `terms.html` (`/terms`), `404.html`.
- **Динамический копирайт**: `2026-текущий год` (автоматически рассчитывается на всех страницах).
- **Кнопка «Мне повезёт!»**: Мгновенный редирект на первый найденный сайт / DuckDuckGo !lucky.
- **Кнопка поиска**: Векторная SVG-лупа на синей кнопке с надписью «Поиск».
- **Оригинальные логотипы и фавиконки**: Сохранены в `static/images/srpr/logo11w.png` и `static/favicon.ico`.

---

## 🚀 Запуск

### Способ 1: Через батник на Windows
Двойной клик по файлу:
```bat
start.bat
```

### Способ 2: Через терминал
```bash
python server.py --port 8080
```

После запуска откройте в браузере:
```
http://localhost:8080
```
или по локальной сети:
```
http://192.168.x.x:8080
```

---

## 📁 Структура проекта

- `index.html` — Главная страница (Google 2014).
- `search.html` — Страница поисковой выдачи с ротацией 5 баннеров, иконками сайтов, пагинацией и живым поиском.
- `about.html` — Страница «О компании».
- `advertising.html` — Страница «Реклама».
- `settings.html` — Страница «Настройки» с возможностью выключения рекламы.
- `business.html`, `privacy.html`, `terms.html` — Информационные страницы.
- `404.html` — Ретро-страница ошибки 404 Google.
- `server.py` — Python HTTP-сервер со встроенным AST-шаблонизатором для локального/VPS запуска.
- `start.bat` — Скрипт быстрого запуска для Windows.
- `static/`
  - `style.css` — Ретро-стили с поддержкой IE6.
  - `favicon.ico` — Фавиконка.
  - `images/srpr/logo11w.png` — Классический логотип Google.
- `test_server.py` — Автоматические тесты Python сервера.
