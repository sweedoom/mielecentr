/* ============================================================================
 *  Админка заявок (общая для обоих сайтов). Загружается как
 *  <script src="assets/admin-app.js" defer></script> после инлайнового
 *  <script>window.ADMIN_CFG = {...}</script>.
 *
 *  Контракт доступа (всё ограничено на СЕРВЕРЕ, клиентские проверки — только UX):
 *    вход    : POST {url}/auth/v1/token?grant_type=password
 *    сайт    : POST {url}/rest/v1/rpc/current_site      -> "holodok" | "mielecentr"
 *    список  : GET  {url}/rest/v1/leads?select=...&site=eq.<site>&order=created_at.desc
 *    правка  : PATCH {url}/rest/v1/leads?id=eq.<id>&site=eq.<site>&select=id,status,comment
 *              с Prefer: return=representation -> ответ подтверждает, что строка обновлена
 *    создание: POST {submitUrl} с Bearer access-токеном и request_id (uuid)
 *    удаления НЕТ: архивация = status = "cancel".
 *
 *  RLS на стороне БД остаётся единственным источником правды: даже если
 *  подменить site в этом файле, чужие заявки не отдадутся.
 * ==========================================================================*/
(function () {
  "use strict";

  /* ======================= чистые помощники (тестируемые) ================= */

  var STATUS = {
    new: ["Новая", "new"],
    work: ["В работе", "work"],
    done: ["Завершена", "done"],
    cancel: ["Отменена", "cancel"],
  };

  var SELECT_COLS = "id,created_at,name,phone,message,source,page,status,comment,site";
  var UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function statusOf(v) {
    return Object.prototype.hasOwnProperty.call(STATUS, v) ? v : "new";
  }

  function isUuid(v) {
    return typeof v === "string" && UUID_RE.test(v);
  }

  /* UUID v4. request_id обязан быть uuid (сервер отклоняет остальное). */
  function uuid() {
    if (typeof crypto !== "undefined" && crypto && typeof crypto.randomUUID === "function") {
      try { return crypto.randomUUID(); } catch (e) { /* ниже запасной путь */ }
    }
    var b = [];
    for (var i = 0; i < 16; i += 1) b.push(Math.floor(Math.random() * 256));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var h = b.map(function (x) { return (x + 0x100).toString(16).slice(1); }).join("");
    return h.slice(0, 8) + "-" + h.slice(8, 12) + "-" + h.slice(12, 16) +
      "-" + h.slice(16, 20) + "-" + h.slice(20);
  }

  function fmt(d) {
    if (!d) return "—";
    var x = new Date(d);
    if (isNaN(x)) return "—";
    var p = function (n) { return n < 10 ? "0" + n : "" + n; };
    return p(x.getDate()) + "." + p(x.getMonth() + 1) + "." + x.getFullYear() +
      " " + p(x.getHours()) + ":" + p(x.getMinutes());
  }

  /* Только http/https/mailto/tel. Всё остальное — включая javascript:,
     data:, vbscript: и попытки спрятать схему за пробелами/переводами строк —
     считается небезопасным и не превращается в ссылку. */
  function safeUrl(raw) {
    var s = String(raw == null ? "" : raw);
    s = s.replace(/[\u0000-\u001f\u007f-\u009f]/g, "").trim();
    if (!s) return "";
    return /^(https?:\/\/|mailto:|tel:)/i.test(s) ? s : "";
  }

  function safeTel(raw) {
    var d = String(raw == null ? "" : raw).replace(/[^\d+]/g, "");
    var digits = d.replace(/\D/g, "");
    if (digits.length < 5 || digits.length > 20) return "";
    return "tel:" + (d.charAt(0) === "+" ? "+" : "") + digits;
  }

  /* Защита от формул в Excel/LibreOffice/Google Sheets: значение, начинающееся
     с = + - @ или с таба/CR, исполняется как формула. Ставим апостроф. */
  function csvCell(v) {
    var s = String(v == null ? "" : v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }

  function normalizeCfg(raw) {
    var c = raw || {};
    var url = String(c.supabaseUrl || "").replace(/\/+$/, "");
    var key = String(c.supabaseAnonKey || "");
    var site = String(c.site || "").trim();
    var looksFake = function (s) { return !s || /REPLACE/i.test(s); };
    return {
      site: site,
      sourceName: String(c.sourceName || site),
      phone: String(c.phone || ""),
      url: url,
      key: key,
      submitUrl: String(c.submitUrl || "") ||
        (url && site ? url + "/functions/v1/leads-" + site : ""),
      ok: !looksFake(url) && !looksFake(key) && !!site && /^https?:\/\//i.test(url),
    };
  }

  function messageForError(err) {
    var m = (err && (err.code || err.message)) || "";
    if (m === "bad_credentials") return "Неверный email или пароль.";
    if (m === "unauthorized" || m === "no_session") return "Нет доступа. Войдите заново.";
    if (m === "session_expired") return "Сессия истекла — войдите снова.";
    if (m === "no_membership") return "Учётная запись не привязана ни к одному сайту. Обратитесь к владельцу сервиса.";
    if (/^wrong_site/.test(m)) return "Этот аккаунт привязан к другому сайту — здесь он прав не имеет.";
    if (m === "network") return "Нет связи с сервером. Проверьте интернет и попробуйте снова.";
    if (m === "rate_limited") return "Слишком много заявок. Попробуйте позже.";
    if (m === "invalid_phone") return "Телефон указан не полностью.";
    if (m === "consent_required") return "Нет согласия на обработку данных.";
    if (m === "payload_too_large") return "Слишком длинный текст заявки.";
    if (m === "forbidden_site") return "Приёмник отклонил запрос: другой сайт.";
    if (m === "patch_not_applied" || m === "patch_wrong_row")
      return "Сервер не подтвердил сохранение — обновите список.";
    if (m === "storage_error" || m === "site_check_failed")
      return "Сервер временно недоступен. Попробуйте ещё раз.";
    if (/^list_failed_(\d+)/.test(m)) return "Не удалось загрузить заявки (код " + m.split("_").pop() + ").";
    if (m === "list_bad_shape" || m === "list_bad_json") return "Сервер вернул неожиданный ответ.";
    return "Что-то пошло не так. Попробуйте ещё раз.";
  }

  var Pure = {
    esc: esc,
    statusOf: statusOf,
    isUuid: isUuid,
    uuid: uuid,
    fmt: fmt,
    safeUrl: safeUrl,
    safeTel: safeTel,
    csvCell: csvCell,
    normalizeCfg: normalizeCfg,
    messageForError: messageForError,
    STATUS: STATUS,
    SELECT_COLS: SELECT_COLS,
  };

  /* Экспорт для тестов (в браузере module не определён — просто пропускаем). */
  if (typeof module !== "undefined" && module.exports) module.exports = Pure;

  if (typeof document === "undefined") return;   /* тестовый/не-DOM контекст */

  /* ============================ состояние ================================= */
  var CFG = normalizeCfg(window.ADMIN_CFG);
  var SESSION_KEY = "leads_admin_session_" + (CFG.site || "site");
  var E = {};                                  /* кэш элементов */
  var session = null;
  var epoch = 0;                               /* растёт при выходе: гасит «догоняющие» ответы */
  var ALL = [];
  var VIEW = [];
  var filter = { status: "", q: "", src: "", sort: "desc" };
  var current = null;
  var loginBusy = false;
  var addBusy = false;
  var drawerBusy = false;
  var pendingRequestId = null;                 /* сохраняется между повторами создания */

  function $(sel) { return E[sel] || (E[sel] = document.querySelector(sel)); }
  function setText(sel, v) { var el = $(sel); if (el) el.textContent = v; }
  function setHTML(sel, v) { var el = $(sel); if (el) el.innerHTML = v; }
  function toast(msg) {
    var t = $("#toast");
    if (!t) return;
    t.textContent = msg;
    t.classList.add("on");
    clearTimeout(t._t);
    t._t = setTimeout(function () { t.classList.remove("on"); }, 3200);
  }
  function alive(ep) { return ep === epoch; }

  /* ============================ сессия ==================================== */
  function saveSession(s) {
    session = s;
    try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(s)); } catch (e) { /* ignore */ }
  }
  function loadSession() {
    try {
      var raw = sessionStorage.getItem(SESSION_KEY);
      session = raw ? JSON.parse(raw) : null;
    } catch (e) { session = null; }
    if (session && (!session.access_token || !session.refresh_token)) session = null;
    return session;
  }
  function clearSession() {
    session = null;
    try { sessionStorage.removeItem(SESSION_KEY); } catch (e) { /* ignore */ }
  }

  /* Заголовки собираются КАЖДЫЙ раз: после refresh берётся новый токен. */
  function restHeaders() {
    return {
      apikey: CFG.key,
      authorization: "Bearer " + (session ? session.access_token : ""),
      "content-type": "application/json",
    };
  }

  async function signIn(email, password) {
    var r;
    try {
      r = await fetch(CFG.url + "/auth/v1/token?grant_type=password", {
        method: "POST",
        headers: { apikey: CFG.key, "content-type": "application/json" },
        body: JSON.stringify({ email: email, password: password }),
      });
    } catch (e) { throw new Error("network"); }
    if (r.status === 400 || r.status === 401) throw new Error("bad_credentials");
    if (!r.ok) throw new Error("storage_error");
    var j = null;
    try { j = await r.json(); } catch (e) { j = null; }
    if (!j || !j.access_token) throw new Error("bad_credentials");
    saveSession({
      access_token: j.access_token,
      refresh_token: j.refresh_token,
      expires_at: Date.now() + (Number(j.expires_in || 3600) - 60) * 1000,
      email: email,
    });
    return session;
  }

  async function refreshSession() {
    if (!session || !session.refresh_token) return false;
    var r;
    try {
      r = await fetch(CFG.url + "/auth/v1/token?grant_type=refresh_token", {
        method: "POST",
        headers: { apikey: CFG.key, "content-type": "application/json" },
        body: JSON.stringify({ refresh_token: session.refresh_token }),
      });
    } catch (e) { return false; }
    if (!r.ok) return false;
    var j = null;
    try { j = await r.json(); } catch (e) { j = null; }
    if (!j || !j.access_token) return false;
    saveSession({
      access_token: j.access_token,
      refresh_token: j.refresh_token || session.refresh_token,
      expires_at: Date.now() + (Number(j.expires_in || 3600) - 60) * 1000,
      email: session ? session.email : "",
    });
    return true;
  }

  /* Подтверждение сайта: спрашиваем у БД, к какому сайту приписан пользователь.
     Это отсекает вход под чужой админкой; RLS при этом остаётся главным
     ограничителем — данные другого сайта не вернутся даже так. */
  async function assertSite() {
    if (!session) throw new Error("no_session");
    var r;
    try {
      r = await fetch(CFG.url + "/rest/v1/rpc/current_site", {
        method: "POST",
        headers: restHeaders(),
        body: "{}",
      });
    } catch (e) { throw new Error("network"); }
    if (r.status === 401 || r.status === 403) throw new Error("unauthorized");
    if (!r.ok) throw new Error("site_check_failed");
    var t = "";
    try { t = await r.text(); } catch (e) { t = ""; }
    var v = null;
    try { v = t ? JSON.parse(t) : null; } catch (e) { v = t; }
    if (v && typeof v === "object") v = v.current_site;
    v = typeof v === "string" ? v.trim() : "";
    if (!v) throw new Error("no_membership");
    if (v !== CFG.site) throw new Error("wrong_site:" + v);
    return v;
  }

  async function verifySession() {
    if (!session) throw new Error("no_session");
    if (session.expires_at && Date.now() > session.expires_at) {
      if (!(await refreshSession())) throw new Error("session_expired");
    }
    await assertSite();
  }

  /* Единая обёртка: обновляем токен на 401, ПОСЛЕ обновления заново
     подтверждаем сайт и повторяем запрос с ПЕРЕСОБРАННЫМИ заголовками. */
  async function withAuth(fn) {
    if (!session) throw new Error("no_session");
    if (session.expires_at && Date.now() > session.expires_at) {
      if (!(await refreshSession())) throw new Error("session_expired");
      await assertSite();
    }
    var res;
    try { res = await fn(); } catch (e) { throw new Error("network"); }
    if (res && res.status === 401) {
      if (!(await refreshSession())) throw new Error("unauthorized");
      await assertSite();
      try { res = await fn(); } catch (e) { throw new Error("network"); }
    }
    return res;
  }

  /* ============================ данные ==================================== */
  async function loadLeads() {
    var ep = epoch;
    var url = CFG.url + "/rest/v1/leads?select=" + encodeURIComponent(SELECT_COLS) +
      "&site=eq." + encodeURIComponent(CFG.site) + "&order=created_at.desc";
    var r = await withAuth(function () { return fetch(url, { headers: restHeaders() }); });
    if (!alive(ep)) return null;               /* вышли — ничего не применяем */
    if (!r.ok) throw new Error("list_failed_" + r.status);
    var rows = null;
    try { rows = await r.json(); } catch (e) { rows = null; }
    if (!Array.isArray(rows)) throw new Error("list_bad_shape");
    return rows;
  }

  /* Правка строго двух полей. id и site — в строке запроса, не в теле:
     подделанный id или чужой сайт отсекутся RLS. return=representation
     заставляет сервер вернуть обновлённую строку — её и проверяем. */
  async function patchLead(id, patch) {
    var body = {};
    if (Object.prototype.hasOwnProperty.call(patch, "status")) body.status = patch.status;
    if (Object.prototype.hasOwnProperty.call(patch, "comment")) body.comment = patch.comment;
    if (!Object.keys(body).length) return true;

    var url = CFG.url + "/rest/v1/leads?id=eq." + encodeURIComponent(id) +
      "&site=eq." + encodeURIComponent(CFG.site) +
      "&select=id,status,comment";
    var r = await withAuth(function () {
      return fetch(url, {
        method: "PATCH",
        headers: Object.assign(restHeaders(), { Prefer: "return=representation" }),
        body: JSON.stringify(body),
      });
    });
    if (!r.ok) throw new Error("patch_failed_" + r.status);

    var rows = null;
    try { rows = await r.json(); } catch (e) { rows = null; }
    if (!Array.isArray(rows) || rows.length !== 1) throw new Error("patch_not_applied");
    var row = rows[0];
    if (String(row.id) !== String(id)) throw new Error("patch_wrong_row");
    if (Object.prototype.hasOwnProperty.call(body, "status") && row.status !== body.status) {
      throw new Error("patch_not_applied");
    }
    if (Object.prototype.hasOwnProperty.call(body, "comment") &&
        String(row.comment == null ? "" : row.comment) !== String(body.comment)) {
      throw new Error("patch_not_applied");
    }
    return true;
  }

  /* Ручное создание — через тот же приёмник, что и формы сайта.
     request_id передаётся снаружи: повтор после сетевого сбоя использует тот же
     id, и сервер вернёт duplicate вместо второй заявки. */
  async function createLead(rec, requestId) {
    if (!isUuid(requestId)) throw new Error("invalid_request_id");
    var payload = {
      request_id: requestId,
      name: rec.name || "",
      phone: rec.phone || "",
      message: rec.message || "",
      source: "Добавлено вручную",
      page: (typeof location !== "undefined" ? location.href : ""),
      consent: true,
      website: "",
    };
    var r = await withAuth(function () {
      return fetch(CFG.submitUrl, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: "Bearer " + session.access_token,
        },
        body: JSON.stringify(payload),
      });
    });
    var j = null;
    try { j = await r.json(); } catch (e) { j = null; }
    if (!r.ok || !j || j.ok !== true) {
      var e = new Error((j && j.error) || ("submit_failed_" + r.status));
      e.code = (j && j.error) || ("http_" + r.status);
      e.status = r.status;
      throw e;
    }
    return j;
  }

  /* ============================ отрисовка ================================= */
  function card(cls, k, v) {
    return '<div class="card ' + cls + '"><div class="k">' + k + '</div><div class="v">' + v + "</div></div>";
  }

  function renderCards() {
    var t = ALL.length, n = 0, w = 0, d = 0, today = 0;
    var day = new Date(); day.setHours(0, 0, 0, 0);
    ALL.forEach(function (l) {
      var s = statusOf(l.status);
      if (s === "new") n += 1; else if (s === "work") w += 1; else if (s === "done") d += 1;
      var x = new Date(l.created_at || 0);
      if (!isNaN(x) && x >= day) today += 1;
    });
    setHTML("#cards", card("a", "Всего заявок", t) + card("n", "Новые", n) +
      card("w", "В работе", w) + card("d", "Завершено", d) + card("", "За сегодня", today));
  }

  function pageHtml(p) {
    if (!p) return "—";
    var u = safeUrl(p);
    if (!u) return esc(p) + ' <span class="hint">(ссылка скрыта: небезопасная схема)</span>';
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(p) + "</a>";
  }

  function applyFilter() {
    var q = filter.q.toLowerCase().trim();
    VIEW = ALL.filter(function (l) {
      if (filter.status && statusOf(l.status) !== filter.status) return false;
      if (filter.src && (l.source || "") !== filter.src) return false;
      if (q) {
        var s = ((l.name || "") + " " + (l.phone || "") + " " + (l.message || "") +
          " " + (l.comment || "")).toLowerCase();
        if (s.indexOf(q) === -1) return false;
      }
      return true;
    });
    VIEW.sort(function (a, b) {
      var x = new Date(a.created_at || 0), y = new Date(b.created_at || 0);
      return filter.sort === "asc" ? x - y : y - x;
    });
    renderTable();
  }

  function renderTable() {
    var tb = $("#tbody");
    var empty = $("#empty");
    if (!VIEW.length) {
      tb.innerHTML = "";
      if (empty) empty.classList.remove("hide");
      return;
    }
    if (empty) empty.classList.add("hide");
    tb.innerHTML = VIEW.map(function (l) {
      var s = STATUS[statusOf(l.status)];
      var tel = safeTel(l.phone);
      return '<tr data-id="' + esc(l.id) + '">' +
        '<td class="dt">' + fmt(l.created_at) + "</td>" +
        "<td>" + (esc(l.name) || '<span style="color:#9aa1ab">—</span>') + "</td>" +
        '<td class="ph"><b>' + (tel
          ? '<a href="' + esc(tel) + '">' + esc(l.phone) + "</a>"
          : esc(l.phone || "—")) + "</b></td>" +
        '<td class="msg">' + (esc(l.message) || "—") + "</td>" +
        "<td>" + esc(l.source || "—") + "</td>" +
        '<td><span class="st ' + s[1] + '">' + s[0] + "</span></td>" +
        '<td class="acts"><button class="btn sm" data-act="open" type="button">Открыть</button></td>' +
        "</tr>";
    }).join("");
  }

  function fillSources() {
    var srcs = {};
    ALL.forEach(function (l) { if (l.source) srcs[l.source] = 1; });
    var sel = $("#fSrc");
    if (!sel) return;
    var cur = sel.value;
    sel.innerHTML = '<option value="">Все формы</option>' + Object.keys(srcs).sort()
      .map(function (v) { return '<option value="' + esc(v) + '">' + esc(v) + "</option>"; })
      .join("");
    sel.value = cur;
  }

  function render() {
    renderCards();
    fillSources();
    applyFilter();
  }

  /* ============================ карточка заявки =========================== */
  function kv(k, v) { return '<div class="kv"><span>' + k + "</span><b>" + v + "</b></div>"; }

  function openLead(id) {
    current = ALL.filter(function (l) { return String(l.id) === String(id); })[0] || null;
    if (!current) return;
    var l = current;
    var st = statusOf(l.status);
    setText("#dTitle", l.name || l.phone || "Заявка");
    setHTML("#dBody",
      kv("Дата", fmt(l.created_at)) +
      kv("Имя", esc(l.name) || "—") +
      kv("Телефон", safeTel(l.phone)
        ? '<a href="' + esc(safeTel(l.phone)) + '">' + esc(l.phone) + "</a>"
        : esc(l.phone || "—")) +
      kv("Сообщение", esc(l.message) || "—") +
      kv("Форма", esc(l.source) || "—") +
      kv("Страница", pageHtml(l.page)) +
      kv("Статус", '<span class="st ' + STATUS[st][1] + '">' + STATUS[st][0] + "</span>"));
    $("#dComment").value = l.comment || "";
    $("#dStatus").value = st;
    $("#drawer").classList.remove("hide");
    $("#shade").classList.remove("hide");
  }

  function closeDrawer() {
    current = null;
    $("#drawer").classList.add("hide");
    $("#shade").classList.add("hide");
    setHTML("#dBody", "");
    $("#dComment").value = "";
  }

  /* Комментарий НЕ теряется при сбое: карточка остаётся открытой с тем же
     текстом, а current не меняется до подтверждения сервером. */
  async function saveDrawer() {
    if (drawerBusy || !current) return;
    var ep = epoch;
    var id = current.id;
    var nextComment = $("#dComment").value;
    var nextStatus = $("#dStatus").value;
    var jobs = [];
    if (nextComment !== (current.comment || "")) jobs.push(patchLead(id, { comment: nextComment }));
    if (nextStatus !== statusOf(current.status)) jobs.push(patchLead(id, { status: nextStatus }));
    if (!jobs.length) { closeDrawer(); return; }

    drawerBusy = true;
    var btns = ["#dSave", "#dCancelStatus", "#dRevert"];
    btns.forEach(function (s) { var b = $(s); if (b) b.disabled = true; });
    try {
      await Promise.all(jobs);
      if (!alive(ep)) return;
      closeDrawer();
      toast("Сохранено");
      await reloadListQuietly(ep);
    } catch (e) {
      /* Сбой сохранения: карточка остаётся открытой, текст комментария —
         в поле, current не подменён (повторная попытка не потеряет правку). */
      if (!alive(ep)) return;
      toast("Не удалось сохранить: " + messageForError(e) + " Текст в форме сохранён.");
    } finally {
      drawerBusy = false;
      btns.forEach(function (s) { var b = $(s); if (b) b.disabled = false; });
    }
  }

  /* Перечитать список после успешной правки. Ошибка чтения не отменяет факт
     сохранения — просто просим нажать «Обновить». */
  async function reloadListQuietly(ep) {
    try {
      var rows = await loadLeads();
      if (!rows || !alive(ep)) return;
      ALL = rows;
      render();
    } catch (e) {
      if (alive(ep)) toast("Сохранено, но список не обновился — нажмите «Обновить».");
    }
  }

  async function cancelLeadStatus() {
    if (drawerBusy || !current) return;
    if (!window.confirm("Перевести заявку в «Отменённые»? Данные не удаляются.")) return;
    var ep = epoch;
    var id = current.id;
    drawerBusy = true;
    try {
      await patchLead(id, { status: "cancel" });
      if (!alive(ep)) return;
      closeDrawer();
      toast("Заявка перенесена в «Отменённые»");
      await reloadListQuietly(ep);
    } catch (e) {
      if (!alive(ep)) return;
      toast("Не удалось сохранить: " + messageForError(e));
    } finally { drawerBusy = false; }
  }

  /* ============================ модалка создания ========================== */
  function closeModal() {
    $("#modal").classList.add("hide");
    $("#shade").classList.add("hide");
  }

  function openModal() {
    pendingRequestId = null;
    setText("#mHint", "Заявка сохранится в этом же хранилище, что и заявки с сайта.");
    $("#mName").value = "";
    $("#mPhone").value = "";
    $("#mMsg").value = "";
    $("#modal").classList.remove("hide");
    $("#shade").classList.remove("hide");
    $("#mName").focus();
  }

  async function saveNewLead() {
    if (addBusy) return;                                   /* защита от двойного клика */
    var phone = $("#mPhone").value.trim();
    if ((phone.match(/\d/g) || []).length < 10) { toast("Введите телефон полностью"); return; }

    /* Тот же request_id при повторе: сервер вернёт duplicate, а не вторую заявку. */
    if (!pendingRequestId) pendingRequestId = uuid();

    addBusy = true;
    var ep = epoch;
    var btn = $("#mSave");
    var old = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "Сохраняем…"; }

    try {
      var res = await createLead({
        name: $("#mName").value.trim(),
        phone: phone,
        message: $("#mMsg").value.trim(),
      }, pendingRequestId);

      if (!alive(ep)) return;
      pendingRequestId = null;                             /* успех — новый id на будущее */
      closeModal();
      var rows = await loadLeads();
      if (!rows) return;
      ALL = rows;
      render();
      toast(res && res.duplicate ? "Заявка уже была сохранена" : "Заявка добавлена");
    } catch (e) {
      if (!alive(ep)) return;
      var code = (e && (e.code || e.message)) || "";
      if (e && (e.status === 401 || code === "unauthorized" || code === "no_session" || code === "session_expired")) {
        forceLogout("Сессия истекла — войдите снова");
        return;
      }
      if (!e || !e.status) {
        toast("Сеть недоступна. Нажмите «Сохранить» ещё раз — дубликата не будет.");
      } else {
        toast("Не удалось добавить: " + messageForError(e));
      }
      /* Модалка остаётся открытой, request_id сохраняется для повторной попытки. */
    } finally {
      addBusy = false;
      if (btn) { btn.disabled = false; btn.textContent = old || "Сохранить"; }
    }
  }

  /* ============================ CSV ======================================= */
  function exportCsv() {
    if (!VIEW.length) { toast("Нечего экспортировать"); return; }
    var head = ["Дата", "Имя", "Телефон", "Сообщение", "Форма", "Статус", "Комментарий"];
    var lines = [head.map(csvCell).join(";")];
    VIEW.forEach(function (l) {
      lines.push([
        fmt(l.created_at), l.name || "", l.phone || "", l.message || "",
        l.source || "", STATUS[statusOf(l.status)][0], l.comment || "",
      ].map(csvCell).join(";"));
    });
    var blob = new Blob(["\ufeff" + lines.join("\r\n")], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "leads-" + (CFG.site || "site") + "-" +
      new Date().toISOString().slice(0, 10) + ".csv";
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  /* ============================ экраны ==================================== */
  function showLogin(msg) {
    setText("#loginErr", msg || "");
    $("#app").classList.add("hide");
    $("#login").classList.remove("hide");
  }
  function showApp() {
    setText("#loginErr", "");
    $("#login").classList.add("hide");
    $("#app").classList.remove("hide");
    $("#password").value = "";
  }

  /* Полная зачистка данных из DOM: после выхода чужие заявки не должны
     оставаться ни в таблице, ни в карточке, ни в полях. */
  function wipeData() {
    ALL = [];
    VIEW = [];
    current = null;
    pendingRequestId = null;
    setHTML("#tbody", "");
    setHTML("#cards", "");
    setHTML("#dBody", "");
    setText("#dTitle", "Заявка");
    var fs = $("#fSrc"); if (fs) fs.innerHTML = '<option value="">Все формы</option>';
    var fst = $("#fStatus"); if (fst) fst.value = "";
    var q = $("#q"); if (q) q.value = "";
    var srt = $("#sort"); if (srt) srt.value = "desc";
    var c = $("#dComment"); if (c) c.value = "";
    var ds = $("#dStatus"); if (ds) ds.value = "new";
    $("#empty").classList.add("hide");
    filter = { status: "", q: "", src: "", sort: "desc" };
  }

  function forceLogout(msg) {
    epoch += 1;                 /* все «догоняющие» ответы становятся недействительными */
    clearSession();
    closeDrawer();
    closeModal();
    $("#shade").classList.add("hide");
    wipeData();
    $("#password").value = "";
    $("#email").value = "";
    showLogin(msg || "");
  }

  /* ============================ вход ====================================== */
  async function doLogin() {
    if (loginBusy) return;
    loginBusy = true;
    var btn = $("#loginBtn");
    var old = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "Входим…"; }
    setText("#loginErr", "");

    var email = $("#email").value.trim();
    var password = $("#password").value;
    try {
      await signIn(email, password);
      await verifySession();          /* сверяем сайт с CFG.site до показа данных */
      var rows = await loadLeads();   /* приложение показываем ТОЛЬКО после успешной загрузки */
      if (!rows) throw new Error("session_expired");
      ALL = rows;
      $("#password").value = "";      /* пароль в DOM не держим */
      showApp();
      render();
    } catch (e) {
      clearSession();
      $("#password").value = "";
      showLogin(messageForError(e));
      var pe = $("#password"); if (pe) pe.focus();
    } finally {
      loginBusy = false;
      if (btn) { btn.disabled = false; btn.textContent = old || "Войти"; }
    }
  }

  async function boot() {
    if (!CFG.ok) {
      showLogin("Панель не настроена: в ADMIN_CFG не заданы site, supabaseUrl или supabaseAnonKey.");
      return;
    }
    setText("#siteChip", CFG.sourceName || CFG.site);
    if (loadSession()) {
      try {
        await verifySession();
        var rows = await loadLeads();
        if (!rows) return;
        ALL = rows;
        showApp();
        render();
        return;
      } catch (e) {
        clearSession();
        showLogin(messageForError(e));
        return;
      }
    }
    showLogin("");
  }

  /* ============================ события =================================== */
  $("#tbody").addEventListener("click", function (e) {
    var tr = e.target.closest("tr");
    if (!tr || !e.target.closest("[data-act]")) return;
    openLead(tr.getAttribute("data-id"));
  });

  $("#loginForm").addEventListener("submit", function (e) {
    e.preventDefault();
    doLogin();
  });
  $("#btnLogout").addEventListener("click", function () { forceLogout("Вы вышли из панели."); });

  $("#btnRefresh").addEventListener("click", async function () {
    var ep = epoch;
    try {
      var rows = await loadLeads();
      if (!rows || !alive(ep)) return;
      ALL = rows;
      render();
      toast("Обновлено");
    } catch (e) {
      if (!alive(ep)) return;
      if (e.message === "unauthorized" || e.message === "session_expired" || e.message === "no_session") {
        forceLogout("Сессия истекла — войдите снова");
        return;
      }
      toast(messageForError(e));
    }
  });

  $("#q").addEventListener("input", function () { filter.q = this.value; applyFilter(); });
  $("#fStatus").addEventListener("change", function () { filter.status = this.value; applyFilter(); });
  $("#fSrc").addEventListener("change", function () { filter.src = this.value; applyFilter(); });
  $("#sort").addEventListener("change", function () { filter.sort = this.value; applyFilter(); });
  $("#btnCsv").addEventListener("click", exportCsv);

  $("#dClose").addEventListener("click", closeDrawer);
  $("#dRevert").addEventListener("click", closeDrawer);
  $("#shade").addEventListener("click", function () {
    if (!$("#modal").classList.contains("hide")) closeModal();
    else closeDrawer();
  });
  $("#dSave").addEventListener("click", saveDrawer);
  $("#dCancelStatus").addEventListener("click", cancelLeadStatus);

  $("#btnAdd").addEventListener("click", openModal);
  $("#mClose").addEventListener("click", closeModal);
  $("#mSave").addEventListener("click", saveNewLead);
  $("#modal").addEventListener("click", function (e) { if (e.target === this) closeModal(); });
  $("#mPhone").addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); saveNewLead(); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if ($("#modal").classList.contains("hide") === false) { closeModal(); return; }
    if ($("#drawer").classList.contains("hide") === false) closeDrawer();
  });

  boot();
})();
