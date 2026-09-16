# ПРОЕКТ: лендинг «ремонт техники Miele в Москве» — ООО «ХОЛОД-ОК»

> Документ для быстрого входа. Читай сверху вниз. Владелец — **не программист**,
> всё делается копированием команд. Если что-то непонятно — читай раздел «Грабли».

---

## 1. Что это

Одностраничный лендинг (static site: HTML + CSS + JS + картинки, без своего сервера).
Скопирован с `msk.mielecentr.ru` (Битрикс, шаблон `gvozdevsoft_master_s1`) и переделан
под ООО «ХОЛОД-ОК».

- **Ниша:** ремонт техники Miele (Миле) — стиралки, холодильники, кофемашины, варочные
  панели, вытяжки, гладильные системы, духовые шкафы, микроволновки, посудомойки,
  сушилки, промышленная/коммерческая техника (11 категорий).
- **Бренд техники** оставлен «Miele» (как в оригинале); **бренд сервиса** заменён
  на «ХОЛОД-ОК» (вместо «Miele Center»).
- **Город:** Москва.
- **Адрес офиса:** **НЕТ** — работают только с выездом мастера на дом. Все блоки
  с физическим адресом удалены (`#headadr` × 2, `#footer_address`,
  `.hdslide_contact_email`), в инструкциях переписаны шаги 4 и 5.
- **Домен (текущий):** http://linar.me/mielecentr/ (через Cloudflare)
- **Хостинг:** GitHub Pages, репозиторий `sweedoom/mielecentr` (публичный)
- **Рабочая папка:** `G:\SlavaSaitOffer\miele\`

---

## 2. Текущий статус

| Что | Статус |
|---|---|
| Клон страницы со всеми стилями/скриптами/картинками | ✅ |
| Битрикс-ядро снято, jQuery 1.11 + slick + owl + fancybox + inputmask подключены явно | ✅ |
| Бренд → ХОЛОД-ОК, телефон, email | ✅ |
| Адрес офиса (везде) удалён | ✅ |
| Шаг «Привезите технику по адресу» → «Мастер выезжает бесплатно*» | ✅ |
| Чужие счётчики (Y.Metrika, Calltouch, bitrix.info ba, Quizgo) вырезаны | ✅ |
| Политика, согласие, 404, robots.txt, sitemap.xml, страница «Реквизиты» | ✅ |
| Заявки → Telegram-бот @slavakrutoislds83_bot | ✅ работает напрямую из браузера |
| Получатели заявок | ✅ 8723283117 + 731734894 (тот же, что в `site/`) |
| Веб-админка через Supabase | ✅ (`admin-a7f3c9.html`, пароль `holodok2026`) |
| Меню «Услуги» / «Контакты» → якоря на этой странице | ✅ |
| «Юридическая информация» (Bitrix popup-link) → `requisites.html` | ✅ |
| «Карта сайта» → удалена | ✅ |
| `check.py` БИТЫХ 0 | ✅ |
| Mobile + Desktop проверены Playwright (0 pageerrors, 0 failed requests) | ✅ |
| Домен под `miele-*` или похожий | ⏳ ждём покупку |

---

## 3. Структура файлов

```
G:\SlavaSaitOffer\miele\
├─ PROJECT.md         ← этот файл — ВСЁ для быстрого входа (отдай другой ИИ)
├─ config.json        ← ВСЕ данные сайта (бренд, телефон, email, тексты)
├─ build.py           ← сборщик: читает config.json, собирает docs/
├─ test.py            ← Playwright smoke-тест (формы, попапы, скриншоты)
├─ policy.py          ← politika.html, soglasie.html, requisites.html
├─ seo.py             ← robots.txt, sitemap.xml, 404.html
├─ render_brand.py    ← og-картинка и favicon (нужен Playwright)
├─ check.py           ← проверка битых локальных ссылок
├─ deploy.sh          ← сборка + коммит + пуш на GitHub (через credential helper)
├─ mirror.py          ← качает исходник + ассеты из BX.setCSSList/setJSList
├─ admin_src.html     ← шаблон веб-админки (Supabase + пароль)
├─ supabase.sql       ← SQL для инициализации таблицы `leads` в Supabase
├─ src\               ← исходник-оригинал и ассеты (НЕ ТРОГАТЬ)
└─ docs\              ← ГОТОВЫЙ САЙТ. Именно он уходит на хостинг.
   ├─ index.html
   ├─ admin-a7f3c9.html
   ├─ politika.html, soglasie.html, requisites.html
   ├─ 404.html, robots.txt, sitemap.xml
   ├─ .nojekyll
   └─ bitrix\, upload\, lib\, assets\, favicon.png
```

**Правило:** правим `config.json` → `python build.py` → готовый сайт в `docs/`.
Никогда не правим файлы в `docs/` руками — они перезапишутся при следующей сборке.

---

## 4. Как собрать и задеплоить

```bash
cd G:/SlavaSaitOffer/miele
python check.py        # проверить битые ссылки (должно быть 0)
python build.py        # пересобрать docs/
bash deploy.sh         # сборка + коммит + пуш на GitHub Pages
```

Сайт обновляется на `linar.me/mielecentr` через 1–2 минуты после пуша.

`deploy.sh` не использует `gh` CLI — он протух. Вместо этого:
1. `git push` идёт через credential helper (`gh auth git-credential` хранит токен).
2. Если репо ещё нет — создаётся руками через `curl` к `api.github.com` с этим
   токеном (`git credential fill` отдаёт `gho_...`). Pages включается тоже через API.
3. После покупки домена и привязки: положить `domain` в `config.json`, `build.py`
   создаст `docs/CNAME`.

---

## 5. Какие данные лежат (config.json)

| Ключ | Что это |
|---|---|
| `brand` | Название (ХОЛОД-ОК) — в лого, title, текстах |
| `brandSlug` | Краткое имя для URL/папок (`holodok`) |
| `siteUrl` | Канонический адрес сайта |
| `domain` | Кастомный домен (CNAME) — пусто, пока не куплен |
| `phonePretty` / `phoneRaw` | Телефон в красивом и цифровом виде |
| `email` | Почта |
| `city` | `nom Москва`, `gen Москвы`, `prep Москве`, `acc Москву`, `abl Москвой` |
| `address` | Пусто — все блоки адреса вырезаются (выезд мастера на дом) |
| `workHours` / `openingHours` | Текстом и для schema.org |
| `geo` | Координаты карты (пока не используются — на странице нет карты) |
| `rating` / `reviews` | Рейтинг 4.9 и число оценок |
| `logo` | `assets/logo.svg` — генерится `build.py` |
| `favicon` | `favicon.png` — генерится `render_brand.py` |
| `tagline` | Подпись у логотипа |
| `policyDate` | Дата публикации политики |
| `company` | Реквизиты ООО (тот же блок, что в `site/`) |
| `textFixes` | Пары `["было", "стало"]` — критично: первый шаг (про «привезти») **идёт до** вырезания адреса, иначе фраза не совпадёт |
| `navTargets` | Якоря для пунктов меню: «Услуги» → `#uslugi`, «Контакты» → `#footer` |
| `serviceLinks` | Куда ведут карточки «Мы ремонтируем» (`#uslugi`) |
| `internalLinks` | Куда ведут ссылки на несуществующие страницы (`#`) |
| `dropBlocks` | Блоки, вырезаемые из копии (квиз Quizgo) |
| `counters.yandex` / `counters.gtag` | Свои счётчики. Пусто = чужие вырезаны |
| `admin.page` | URL админки (`admin-a7f3c9.html`) |
| `admin.password` | Пароль (`holodok2026`) |
| `admin.supabase` | Project URL + anon public ключ |
| `leads.mode` | `telegram` — заявки летят напрямую из браузера |
| `leads.telegramBotToken` | Токен бота |
| `leads.telegramChatIds` | **Список** ID админов: `["8723283117", "731734894"]` |
| `policyDate` | Дата публикации политики |

---

## 6. Заявки, Telegram и веб-админка

**Заявки идут ДВУМЯ путями параллельно** (как в `site/`):

```
Гость → форма на сайте
          │ 1) Telegram: POST api.telegram.org/bot<TOKEN>/sendMessage
          │    → админам 8723283117 и 731734894
          │ 2) Supabase: POST {url}/rest/v1/leads
          │    → таблица заявок (для веб-админки)
          ▼
       Пользователь видит «Спасибо, заявка отправлена»
```

**Telegram (основной канал):**
- Бот: `@slavakrutoislds83_bot`
- Токен в JS в base64 (браузер декодирует через `atob()`)
- Получатели: `8723283117` + `731734894`

**Supabase (для веб-админки):** используется тот же проект, что и в `site/` —
`wedeflvoryfdkzuodgzg.supabase.co`. Таблица `public.leads` общая для обоих сайтов.

**Админка:** http://linar.me/mielecentr/admin-a7f3c9.html → пароль `holodok2026`.
Внутри нейтральная панель заявок (фильтры, статусы, комментарии, CSV, статистика).
**Нет упоминаний Telegram / Supabase / бота** — админ видит только таблицу.

---

## 7. Домен

`config.json → domain` — пусто. Когда купишь:
1. Положи `domain` (например, `miele-remont.ru`) в `config.json → domain`.
2. У DNS-провайдера: A-записи `185.199.108.153` / `185.199.109.153` /
   `185.199.110.153` / `185.199.111.153` на apex, и CNAME `www → sweedoom.github.io`.
3. Запусти `python build.py` (создаст `docs/CNAME`) → `bash deploy.sh`.
4. В настройках репо GitHub Pages custom domain появится как «built»,
   я включу Enforce HTTPS.

---

## 8. Грабли (уже решено — не наступать снова)

1. **Bitrix-ядро в статике.** `core.min.js` / `kernel_main_v1.js` /
   `main.popup.bundle.min.js` / `template_..._v1.js` (агрегат) без BX падают
   с `BX is not defined`. Решение: вырезать, подключить явно
   `jquery-1.11.0.min.js` + slick + owl + fancybox + inputmask + `main.js`.
   Перед `</head>` добавить мини-shim
   `<script>window.BX=window.BX||{message:function(){},ready:function(f){jQuery(f);}};</script>`
   — на случай если кто-то из оставшихся либ дёрнет BX.

2. **CSS/JS подгружаются через `BX.setCSSList/BX.setJSList`.** Обычные `src=`/`href=`
   найдут только 50 ассетов; нужно парсить оба массива и добавлять в очередь загрузки.
   `mirror.py` это делает (включая 2 прохода по CSS для вложенных `url()`).

3. **Fancybox popup-формы.** Fancybox 3 *перемещает* (или клонирует) исходную форму
   в свой контейнер. Submit-обработчик биндить **делегированно**:
   `$(document).on('submit','form.feedback', handler)`. Иначе на закрытии попапа
   обработчик на оригинальной форме уже отвяжется.

4. **`/lib/feedback/feedback.js`** постит форму на `/lib/feedback/mail-form.php`
   (на статике не существует). Решение: вырезать, обрабатывать формы своими силами.

5. **`/bitrix/components/custom/popup.link/script.js`** использует BX.PopupWindowManager
   + AJAX к `/bitrix/tools/custom.popup/ajax.php`. Решение: вырезать, ссылку
   «Юридическая информация» перевести на `requisites.html`.

6. **`<div class="b-quizgo-quiz-block">`** + `//panel.quizgo.ru/common?q=84181` —
   сторонний квиз-сервис, на статике не работает. Вырезать и div, и script.

7. **Удаление адреса + textFixes — порядок важен.** Шаг 4 в инструкциях содержит
   адрес («г. Москва, Учительская, 16Б»). Если сначала вырезать адрес, а потом
   прогнать `textFixes` — фраза уже не совпадёт, build.py молча пропустит
   (логирует «НЕ НАЙДЕНО»). Решение: textFixes прогоняются **до** вырезания адреса.

8. **Пустой `address` в config** — нужно убрать три типа блоков: `<div id="headadr">`
   (бывает 2 штуки — в шапке и в мобильной панели), `<div id="footer_address">`,
   `<div class="hdslide_contact_email">`. Все — в `build.py → step 12` (`addr`).

9. **404 на одном сервис-боксе.** В исходнике есть закомментированный блок
   «Ремонт техники Miele в Санкт-Петербурге» с картинкой, которой 404 на оригинале.
   `check.py` парсит HTML как есть, поэтому игнорируем ссылки внутри `<!-- ... -->`.

10. **Cloudflare редирект `linar.me/<repo>`.** Для нового репо Cloudflare (если
    настроен шаблон) автоматически перенаправляет `sweedoom.github.io/<repo>` на
    `linar.me/<repo>`. Не нужно вручную прописывать — просто пушь в новый репо,
    и Cloudflare подхватит.

11. **`<div class="title">` снаружи `<form>`.** У основной формы заголовок
    «Нужна консультация специалиста?» находится в `<div class="text">`,
    а сама форма — соседний `<form>`. После успешной отправки наш handler
    не найдёт `.title` внутри формы. Решение: если `.title` не найден —
    `form.prepend(thanks)`.

12. **GitHub Pages html_url.** При создании Pages через API GH автоматически
    выставляет `html_url: http://linar.me/mielecentr/` (берёт из Cloudflare?).
    Это **не** CNAME — ничего страшного, но 301 c `github.io` на `linar.me`
    может удивить.

---

## 9. Частые задачи

| Задача | Что делать |
|---|---|
| Поменять телефон | `config.json` → `phonePretty`, `phoneRaw` → `python build.py` → `bash deploy.sh` |
| Поменять email | `config.json` → `email` → пересборка |
| Поменять город | `config.json` → `city` (все 5 падежей!) → пересборка |
| Изменить текст | `config.json` → `textFixes`: `["старый", "новый"]` |
| Добавить/убрать пункт меню | `config.json` → `navTargets` |
| Убрать другой блок | `config.json` → `dropBlocks`: `["div.имя_класса"]` |
| Подключить свой счётчик | `config.json` → `counters.yandex: ["12345678"]` или `counters.gtag: "G-XXXXXXX"` |
| Посмотреть заявки | Telegram, чат с ботом |
| Заявки в веб-админке | http://linar.me/mielecentr/admin-a7f3c9.html |
| Привязать домен | См. §7 |
| Откатить всё | `git log` → `git checkout <хеш> -- .` → `python build.py` |

---

## 10. Контакты и доступы

- GitHub: `sweedoom` (репо `mielecentr`)
- Текущий домен: `linar.me/mielecentr`
- Владелец: Мамченко Линар Сергеевич, `esquirecypherx@mail.ru`, Челябинск
- Telegram админа: `8723283117` (активен) + `731734894` (нужен /start)
- Telegram-бот: `@slavakrutoislds83_bot`
- Токен бота: `8363138970:AAGIQUiifd0O5bz4qZh4GRzIXTBNU7f29aA`
- Компания: ООО «ХОЛОД-ОК», ИНН 7452172713, КПП 745201001 (Челябинск)

---

## 11. Чем владелец доволен / не доволен

- ✅ Тот же бренд (ХОЛОД-ОК) и те же контакты — знакомый процесс
- ✅ Miele как бренд техники сохранён
- ✅ Адрес «куда привезти» убран — только выезд
- ✅ Все формы шлют заявки обоим админам в Telegram
- ✅ Админка по тому же URL и с тем же паролем
- ⏳ Ждёт покупку домена (например, `miele-remont.ru` / `mielecentr.ru` / что-то похожее)