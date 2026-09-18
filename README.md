# Nekich Search (Ретро-поиск Google 2014)

Полнофункциональный легковесный поисковик в стиле классического интерфейса **Google 2014 года**, с поддержкой **GitHub Pages** (статический хостинг) и локального/серверного бэкенда на Python, оптимизированный для старых браузеров (Internet Explorer 6, Netscape, Opera и др.) и современных систем.

---

## 🌟 Особенности

- **Ретро-дизайн 2014 года**: Аутентичный чистый внешний вид Google 2014 года.
- **Без `gbar` и без вкладок**: Верхняя панель Google и лишние вкладки удалены.
- **Поиск DuckDuckGo + Wikipedia + Open APIs**: Работает как через Python-сервер, так и прямо в статике на GitHub Pages!
- **5 Ротируемых баннеров с переходами**:
  1. **Inori Aizawa** (`https://faero.top/ad/inori.png`) &rarr; [https://inori.faero.top](https://inori.faero.top)
  2. **LunaStore** (`https://faero.top/ad/ls_rek.png`) &rarr; [https://lunastore.app](https://lunastore.app)
  3. **Renaissance** (`https://faero.top/ad/mrim.jpg`) &rarr; [https://mrim.su](https://mrim.su)
  4. **FaeroFM** (`https://faero.top/ad/faerofm.png`) &rarr; [https://fm.faero.top](https://fm.faero.top)
  5. **faero.top** (`https://faero.top/ad/faero.png`) &rarr; [https://faero.top](https://faero.top)
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

## 🌐 Развертывание на GitHub Pages

Проект полностью готов для публикации на GitHub Pages:

1. **Инициализируйте репозиторий и отправьте код в GitHub**:
   ```bash
   git remote add origin https://github.com/nekxd/Nekich-Search.git
   git branch -M main
   git push -u origin main
   ```

2. **Включите GitHub Pages в настройках репозитория**:
   - Перейдите в **Settings** репозитория на GitHub &rarr; вкладка **Pages**.
   - В разделе **Build and deployment** выберите:
     - **Source**: `Deploy from a branch`
     - **Branch**: `main` / `/(root)`
   - Нажмите **Save**.

3. **Готово!** Ваш поисковик будет доступен по адресу:
   ```
   https://nekxd.github.io/Nekich-Search/
   ```

---

## 💻 Локальный запуск (Python-сервер)

Если вы хотите запустить проект локально с полноценным HTTP-сервером:

### Способ 1: Через батник на Windows
Двойной клик по файлу:
```bat
start.bat
```

### Способ 2: Через терминал
```bash
python server.py --port 8080
```

После запуска откройте:
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
- `search.html` — Страница поисковой выдачи с ротацией 5 баннеров, пагинацией и живым поиском.
- `about.html` — Страница «О компании».
- `advertising.html` — Страница «Реклама».
- `settings.html` — Страница «Настройки» с возможностью выключения рекламы.
- `business.html`, `privacy.html`, `terms.html` — Информационные страницы.
- `404.html` — Ретро-страница ошибки 404 Google.
- `.nojekyll` — Файл отключения Jekyll для корректного хостинга на GitHub Pages.
- `server.py` — Python HTTP-сервер со встроенным AST-шаблонизатором для локального/VPS запуска.
- `start.bat` — Скрипт быстрого запуска для Windows.
- `static/`
  - `style.css` — Ретро-стили с поддержкой IE6.
  - `favicon.ico` — Фавиконка.
  - `images/srpr/logo11w.png` — Классический логотип Google.
- `test_server.py` — Автоматические тесты Python сервера.
