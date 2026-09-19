# -*- coding: utf-8 -*-
"""
frontend.py вЂ” Р»РѕРєР°Р»СЊРЅС‹Рµ РґРѕСЂР°Р±РѕС‚РєРё С„СЂРѕРЅС‚РµРЅРґР° Р»РµРЅРґРёРЅРіР° В«Р РµРјРѕРЅС‚ С‚РµС…РЅРёРєРё MieleВ».

Р•РґРёРЅСЃС‚РІРµРЅРЅР°СЏ С‚РѕС‡РєР° РІС…РѕРґР° РґР»СЏ СЃР±РѕСЂС‰РёРєР°:

    import frontend
    h = frontend.improve_html(h, cfg)

improve_html РІС‹Р·С‹РІР°РµС‚СЃСЏ РџРћРЎР›Р• РІСЃРµС… РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёР№ build.py Рё РџР•Р Р•Р” Р·Р°РїРёСЃСЊСЋ
docs/index.html. Р§С‚Рѕ РѕРЅР° РґРµР»Р°РµС‚:

  * С‡РёСЃС‚РёС‚ <head>: СѓР±РёСЂР°РµС‚ С‚СЏР¶С‘Р»С‹Рµ CSS/JS С€Р°Р±Р»РѕРЅР°-РєРѕРїРёРё, СЃС‚Р°РІРёС‚ РєРѕСЂСЂРµРєС‚РЅС‹Рµ
    title/description, rel=canonical, Open Graph, Twitter, theme-color,
    favicon Рё JSON-LD (С‚РѕР»СЊРєРѕ СЂРµР°Р»СЊРЅС‹Рµ С„Р°РєС‚С‹ вЂ” Р±РµР· РІС‹РґСѓРјР°РЅРЅС‹С… СЂРµР№С‚РёРЅРіРѕРІ,
    РѕС‚Р·С‹РІРѕРІ Рё РїРµСЂСЃРѕРЅР°Р»РёР№);
  * Р·Р°РјРµРЅСЏРµС‚ РІС‘СЂСЃС‚РєСѓ <body> РЅР° С‡РёСЃС‚СѓСЋ Р°РґР°РїС‚РёРІРЅСѓСЋ РєРѕРјРїРѕР·РёС†РёСЋ РІ С„РёСЂРјРµРЅРЅС‹С…
    РєСЂР°СЃРЅРѕ-РіСЂР°С„РёС‚РѕРІРѕ-Р±РµР»С‹С… С‚РѕРЅР°С…: РѕРґРёРЅ <h1>, СЂР°Р±РѕС‡РµРµ РјРѕР±РёР»СЊРЅРѕРµ РјРµРЅСЋ,
    Р°РєРєСѓСЂР°С‚РЅС‹Рµ РєР°СЂС‚РѕС‡РєРё СѓСЃР»СѓРі;
  * РѕСЃС‚Р°РІР»СЏРµС‚ СЂР°Р±РѕС‡РёРµ С„РѕСЂРјС‹ СЃ СЃРµР»РµРєС‚РѕСЂР°РјРё, РєРѕС‚РѕСЂС‹С… Р¶РґС‘С‚ РєР»РёРµРЅС‚ Р·Р°СЏРІРѕРє:
    form.feedback + input[name=form_name || form_phone || form_message]
    Рё РѕР±СЏР·Р°С‚РµР»СЊРЅРѕРµ СЃРѕРіР»Р°СЃРёРµ (checkbox required). РЎР°Рј РєР»РёРµРЅС‚ Р·Р°СЏРІРѕРє
    РїРѕРґРєР»СЋС‡Р°РµС‚ СЂРѕРґРёС‚РµР»СЊ (build.py) вЂ” Р·РґРµСЃСЊ С‚РѕР»СЊРєРѕ СЂР°Р·РјРµС‚РєР°;
  * СЃРѕС…СЂР°РЅСЏРµС‚ Р»РѕРєР°Р»СЊРЅС‹Рµ РєР°СЂС‚РёРЅРєРё СѓСЃР»СѓРі, С‚РµР»РµС„РѕРЅ, e-mail Рё СЂРµРєРІРёР·РёС‚С‹ РћРћРћ.

Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕ: write_assets(out_dir, cfg) вЂ” РѕРїС†РёРѕРЅР°Р»СЊРЅС‹Р№ С…РµР»РїРµСЂ, РµСЃР»Рё
РїРѕРЅР°РґРѕР±РёС‚СЃСЏ РІС‹РЅРµСЃС‚Рё СЃС‚РёР»Рё/СЃРєСЂРёРїС‚ РІ РѕС‚РґРµР»СЊРЅС‹Рµ С„Р°Р№Р»С‹ (РїРѕ СѓРјРѕР»С‡Р°РЅРёСЋ вЂ” inline).
"""

import json
import os
import re
from html import escape as _escape

DEFAULT_ACCENT = "#a3000a"
DEFAULT_ACCENT_DARK = "#7a0008"

# ---------------------------------------------------------------------------
# РЎС‚РёР»Рё. РЎРёРјРІРѕР»С‹-С‚РѕРєРµРЅС‹ __A__ / __AD__ РїРѕРґРјРµРЅСЏСЋС‚СЃСЏ Р°РєС†РµРЅС‚РѕРј РёР· config.json,
# РїРѕСЌС‚РѕРјСѓ СЃС‚СЂРѕРєР° РќР• f-string (РІ CSS РјРЅРѕРіРѕ С„РёРіСѓСЂРЅС‹С… СЃРєРѕР±РѕРє).
# ---------------------------------------------------------------------------
CSS = r"""
*,
*::before,
*::after { box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  font-family: "Segoe UI", Inter, Arial, Helvetica, sans-serif;
  color: #242424;
  background: #fff;
  line-height: 1.55;
}
img { max-width: 100%; height: auto; display: block; }
a { color: inherit; text-decoration: none; }
h1, h2, h3 { margin: 0 0 .55em; line-height: 1.2; color: #1b1b1b; }
p { margin: 0 0 1em; }
ul, ol { margin: 0; }

.fe-wrap { width: 100%; max-width: 1180px; margin: 0 auto; padding: 0 20px; }
.fe-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

/* ---------- РєРЅРѕРїРєРё ---------- */
.fe-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  border: 0; cursor: pointer; font: inherit; font-weight: 600;
  padding: 12px 22px; border-radius: 10px; transition: background .18s, color .18s, box-shadow .18s;
  text-align: center; line-height: 1.2;
}
.fe-btn--accent { background: __A__; color: #fff; }
.fe-btn--accent:hover { background: __AD__; }
.fe-btn--ghost { background: rgba(255,255,255,.12); color: #fff; border: 1px solid rgba(255,255,255,.55); }
.fe-btn--ghost:hover { background: rgba(255,255,255,.24); }
.fe-btn--lg { padding: 15px 30px; font-size: 17px; }

/* ---------- С€Р°РїРєР° ---------- */
.fe-header { position: sticky; top: 0; z-index: 60; background: #fff; border-bottom: 1px solid #e6e6e6; }
.fe-header__in { display: flex; align-items: center; gap: 16px; min-height: 78px; }
.fe-logo { flex: 0 0 auto; display: flex; align-items: center; }
.fe-logo img { height: 46px; width: auto !important; max-width: 210px; }
.fe-nav { display: flex; gap: 4px; margin-left: 6px; }
.fe-nav a { padding: 10px 12px; border-radius: 8px; font-weight: 600; color: #333; white-space: nowrap; }
.fe-nav a:hover { background: #f4f4f5; color: __A__; }
.fe-header__cta { display: flex; align-items: center; gap: 14px; margin-left: auto; }
.fe-phone { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; white-space: nowrap; }
.fe-phone svg { width: 18px; height: 18px; fill: __A__; flex: 0 0 auto; }
.fe-phone:hover { color: __A__; }
.fe-burger {
  display: none; flex-direction: column; justify-content: center; gap: 4px;
  width: 44px; height: 44px; border: 1px solid #e6e6e6; border-radius: 10px; background: #fff; cursor: pointer;
}
.fe-burger span { display: block; width: 22px; height: 2px; margin: 0 auto; border-radius: 2px; background: #1b1b1b; }

/* ---------- РіРµСЂРѕР№ ---------- */
.fe-hero {
  position: relative; color: #fff; background-color: #1b1b1b;
  background-size: cover; background-position: center;
}
.fe-hero__in { padding: 88px 0 96px; max-width: 780px; }
.fe-hero__kicker { text-transform: uppercase; letter-spacing: .12em; font-size: 13px; font-weight: 700; color: #ffc9c9; margin-bottom: 16px; }
.fe-hero h1 { color: #fff; font-size: clamp(26px, 4vw, 46px); margin-bottom: 18px; }
.fe-hero__lead { font-size: clamp(16px, 1.8vw, 20px); color: #efefef; margin-bottom: 26px; }
.fe-hero__cta { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 30px; }
.fe-hero__facts { display: flex; flex-wrap: wrap; gap: 10px 28px; list-style: none; padding: 0; font-size: 15px; color: #e9e9e9; }
.fe-hero__facts li { position: relative; padding-left: 22px; }
.fe-hero__facts li::before { content: ""; position: absolute; left: 0; top: 9px; width: 8px; height: 8px; border-radius: 50%; background: #fff; }

/* ---------- СЃРµРєС†РёРё ---------- */
.fe-sec { padding: 72px 0; }
.fe-sec--soft { background: #f6f6f7; }
.fe-sec h2 { font-size: clamp(22px, 3vw, 34px); }
.fe-sec__sub { color: #6d6d6d; max-width: 780px; }

/* ---------- РєР°СЂС‚РѕС‡РєРё СѓСЃР»СѓРі ---------- */
.fe-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 34px; }
.fe-card { display: flex; flex-direction: column; background: #fff; border: 1px solid #e6e6e6; border-radius: 14px; overflow: hidden; transition: transform .18s, box-shadow .18s, border-color .18s; }
.fe-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(0,0,0,.10); border-color: #dcdcdc; }
.fe-card__img { display: block; aspect-ratio: 16 / 9; overflow: hidden; background: #ededed; }
.fe-card__img img { width: 100%; height: 100%; object-fit: cover; }
.fe-card__t { display: block; padding: 16px 18px; font-weight: 600; color: #1b1b1b; }
.fe-card:hover .fe-card__t { color: __A__; }

/* ---------- РґРІРµ РєРѕР»РѕРЅРєРё / С€Р°РіРё ---------- */
.fe-two { display: grid; grid-template-columns: 1.35fr 1fr; gap: 48px; align-items: start; }
.fe-steps { list-style: none; counter-reset: fe-step; padding: 0; }
.fe-steps li { counter-increment: fe-step; position: relative; padding: 0 0 18px 54px; color: #3a3a3a; }
.fe-steps li::before {
  content: counter(fe-step); position: absolute; left: 0; top: 0;
  width: 34px; height: 34px; border-radius: 50%; background: __A__; color: #fff;
  font-weight: 700; display: flex; align-items: center; justify-content: center;
}
.fe-steps b { color: #1b1b1b; }
.fe-note { background: #fff; border: 1px solid #e6e6e6; border-left: 4px solid __A__; border-radius: 12px; padding: 26px; }
.fe-note p:last-child { margin-bottom: 0; }

/* ---------- Р±Р»РѕРє СЃ С„РѕСЂРјРѕР№ ---------- */
.fe-formsec { background: linear-gradient(135deg, #1b1b1b 0%, #2c2c2c 100%); color: #fff; }
.fe-formsec h2 { color: #fff; }
.fe-formsec__in { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: start; }
.fe-formsec__text a { color: #ffb3b3; text-decoration: underline; }
.fe-formsec__note { font-size: 13px; color: #c9c9c9; margin-top: 18px; }
.fe-form {
  display: flex; flex-direction: column; gap: 14px; color: #242424;
  background: #fff; border-radius: 16px; padding: 26px; box-shadow: 0 16px 40px rgba(0,0,0,.25);
}
.fe-form .title { font-size: 20px; font-weight: 700; color: #1b1b1b; }
.fe-field { display: flex; flex-direction: column; gap: 6px; }
.fe-field > span { font-size: 13px; font-weight: 600; color: #555; }
.fe-form input[type=text],
.fe-form input[type=tel],
.fe-form input[type=email],
.fe-form textarea {
  width: 100%; padding: 13px 14px; border: 1px solid #d9d9d9; border-radius: 10px;
  font: inherit; color: #1b1b1b; background: #fafafa; transition: border-color .15s, box-shadow .15s, background .15s;
}
.fe-form input:focus, .fe-form textarea:focus { outline: none; border-color: __A__; background: #fff; box-shadow: 0 0 0 3px rgba(163,0,10,.12); }
.fe-form textarea { resize: vertical; }
.fe-consent { display: flex; gap: 10px; align-items: flex-start; font-size: 13px; color: #5a5a5a; }
.fe-consent input { width: 18px; height: 18px; margin: 2px 0 0; flex: 0 0 auto; accent-color: __A__; }
.fe-consent a { color: __A__; text-decoration: underline; }
.fe-error { color: #b00020; font-size: 13px; }
.fe-error:empty { display: none; }
.thanks_form { color: __A__; font-weight: 700; padding: 12px 0; }

/* ---------- РїРѕРґРІР°Р» ---------- */
.fe-footer { background: #1b1b1b; color: #cfcfcf; padding-top: 56px; }
.fe-footer__top { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1.1fr; gap: 36px; padding-bottom: 40px; }
.fe-footer__col h3 { color: #fff; font-size: 15px; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 16px; }
.fe-footer__col a { display: block; padding: 4px 0; color: #cfcfcf; }
.fe-footer__col a:hover { color: #fff; }
.fe-footer__col p { margin: 0 0 8px; }
.fe-footer__about { color: #a9a9a9; font-size: 14px; margin-top: 16px; }
.fe-footer img { height: 46px; width: auto !important; max-width: 210px; }
.fe-footer__bottom { border-top: 1px solid #333; padding: 20px 0; font-size: 13px; color: #9a9a9a; }
.fe-footer__bottom .fe-wrap { display: flex; flex-wrap: wrap; gap: 8px 24px; justify-content: space-between; }
.fe-footer .legal { color: #8a8a8a; margin: 0; }

/* ---------- РјРѕРґР°Р»СЊРЅС‹Рµ РѕРєРЅР° ---------- */
.fe-modal { display: none; position: fixed; inset: 0; z-index: 120; align-items: center; justify-content: center; padding: 20px; }
.fe-modal--open { display: flex; }
.fe-modal__ov { position: absolute; inset: 0; background: rgba(17,17,17,.66); }
.fe-modal__box { position: relative; z-index: 2; width: 100%; max-width: 440px; max-height: 92vh; overflow: auto; background: #fff; border-radius: 16px; padding: 26px; box-shadow: 0 24px 60px rgba(0,0,0,.35); }
.fe-modal__x { position: absolute; top: 12px; right: 12px; width: 36px; height: 36px; border: 0; border-radius: 8px; background: #f2f2f2; color: #333; font-size: 22px; line-height: 1; cursor: pointer; }
.fe-modal__x:hover { background: #e6e6e6; }
.fe-modal__sub { color: #666; font-size: 14px; margin: -4px 0 4px; }
.fe-modal .fe-form { padding: 0; box-shadow: none; border-radius: 0; }
html.fe-no-scroll, body.fe-nav-open { overflow: hidden; }

/* ---------- Р°РґР°РїС‚РёРІ ---------- */
@media (max-width: 1024px) {
  .fe-two { grid-template-columns: 1fr; gap: 34px; }
  .fe-formsec__in { grid-template-columns: 1fr; gap: 34px; }
  .fe-footer__top { grid-template-columns: 1fr 1fr; gap: 28px; }
}
@media (max-width: 860px) {
  .fe-header__in { min-height: 66px; gap: 12px; }
  .fe-burger { display: inline-flex; }
  .fe-header__cta .fe-btn { display: none; }
  .fe-logo img { height: 38px; max-width: 170px; }
  .fe-nav {
    position: fixed; top: 66px; left: 0; right: 0; z-index: 55; margin: 0;
    flex-direction: column; gap: 0; padding: 8px 20px 16px; background: #fff;
    border-bottom: 1px solid #e6e6e6; box-shadow: 0 18px 30px rgba(0,0,0,.12);
    transform: translateY(-150%); transition: transform .22s ease;
  }
  body.fe-nav-open .fe-nav { transform: translateY(0); }
  .fe-nav a { padding: 14px 4px; border-bottom: 1px solid #f1f1f1; border-radius: 0; }
  .fe-hero__in { padding: 60px 0 66px; }
  .fe-sec { padding: 52px 0; }
  .fe-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-top: 26px; }
}
@media (max-width: 640px) {
  .fe-phone__num { display: none; }
  .fe-footer__top { grid-template-columns: 1fr; gap: 26px; }
  .fe-form { padding: 20px; }
}
"""

# ---------------------------------------------------------------------------
# РЎРєСЂРёРїС‚: РјРѕР±РёР»СЊРЅРѕРµ РјРµРЅСЋ + СЃРІРѕРё РјРѕРґР°Р»СЊРЅС‹Рµ РѕРєРЅР° (vanilla JS, Р±РµР· jQuery).
# РђРІС‚РѕР·Р°РєСЂС‹С‚РёРµ РјРѕРґР°Р»РєРё РїРѕСЃР»Рµ СѓСЃРїРµС€РЅРѕР№ РѕС‚РїСЂР°РІРєРё: РєР»РёРµРЅС‚ Р·Р°СЏРІРѕРє СЂРѕРґРёС‚РµР»СЏ
# РїРѕРґРјРµРЅСЏРµС‚ СЃРѕРґРµСЂР¶РёРјРѕРµ .title РЅР° .thanks_form вЂ” Р»РѕРІРёРј СЌС‚Рѕ С‡РµСЂРµР· MutationObserver.
# ---------------------------------------------------------------------------
JS = r"""
(function () {
  var body = document.body;

  /* РјРѕР±РёР»СЊРЅРѕРµ РјРµРЅСЋ */
  var burger = document.querySelector('.fe-burger');
  var nav = document.getElementById('fe-nav');
  function closeNav() { body.classList.remove('fe-nav-open'); if (burger) burger.setAttribute('aria-expanded', 'false'); }
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = body.classList.toggle('fe-nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) { if (e.target && e.target.tagName === 'A') closeNav(); });
  }

  /* РјРѕРґР°Р»СЊРЅС‹Рµ РѕРєРЅР° */
  function closeModal(m) {
    if (!m) return;
    m.classList.remove('fe-modal--open');
    m.setAttribute('hidden', '');
    document.documentElement.classList.remove('fe-no-scroll');
  }
  function openModal(sel) {
    var m = document.querySelector(sel);
    if (!m) return;
    m.removeAttribute('hidden');
    m.classList.add('fe-modal--open');
    document.documentElement.classList.add('fe-no-scroll');
    var first = m.querySelector('input, textarea, button');
    if (first) setTimeout(function () { try { first.focus(); } catch (e) {} }, 40);
  }
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var open = t.closest('[data-modal]');
    if (open) { e.preventDefault(); openModal(open.getAttribute('data-modal')); return; }
    var close = t.closest('[data-close]');
    if (close) { e.preventDefault(); closeModal(close.closest('.fe-modal')); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      var list = document.querySelectorAll('.fe-modal--open');
      for (var i = 0; i < list.length; i++) closeModal(list[i]);
    }
  });

  /* Р°РІС‚РѕР·Р°РєСЂС‹С‚РёРµ РјРѕРґР°Р»РєРё РїРѕСЃР»Рµ СѓСЃРїРµС€РЅРѕР№ РѕС‚РїСЂР°РІРєРё */
  var forms = document.querySelectorAll('.fe-modal form');
  for (var i = 0; i < forms.length; i++) {
    (function (f) {
      var t = f.querySelector('.title');
      if (!t || !window.MutationObserver) return;
      new MutationObserver(function () {
        if (f.querySelector('.thanks_form')) {
          setTimeout(function () { closeModal(f.closest('.fe-modal')); }, 1800);
        }
      }).observe(t, { childList: true, subtree: true });
    })(forms[i]);
  }
})();
"""

PHONE_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
             '<path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 '
             '1.1.4 2.3.6 3.5.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 '
             '1-1h3.4c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.5.1.4 0 .8-.2 1z"/></svg>')



DEFAULT_SERVICES = [
    "Ремонт стиральных машин Miele",
    "Ремонт холодильников Miele",
    "Ремонт кофемашин Miele",
    "Ремонт варочных панелей Miele",
    "Ремонт вытяжек Miele",
    "Ремонт гладильных систем Miele",
    "Ремонт духовых шкафов Miele",
    "Ремонт микроволновых печей Miele",
    "Ремонт посудомоечных машин Miele",
    "Ремонт сушильных машин Miele",
    "Ремонт промышленной и коммерческой техники Miele",
]


# ---------------------------------------------------------------------------
# вспомогательное
# ---------------------------------------------------------------------------
def _accent(cfg):
    th = cfg.get("theme") or {}
    a = (th.get("accent") or DEFAULT_ACCENT).strip() or DEFAULT_ACCENT
    ad = (th.get("accentDark") or DEFAULT_ACCENT_DARK).strip() or DEFAULT_ACCENT_DARK
    return a, ad


def _clean_text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.replace("&nbsp;", " ").replace("&laquo;", "\u00ab").replace("&raquo;", "\u00bb")
    return re.sub(r"\s+", " ", s).strip()


def _parse(h, cfg):
    """Достаём из уже преобразованного HTML реальные данные: H1, фон героя, услуги."""
    data = {}
    m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S | re.I)
    data["h1"] = _clean_text(m.group(1)) if m else ""

    m = re.search(r"background-image\s*:\s*url\(\s*['\"]?([^)'\"]+)", h, re.I)
    data["hero"] = m.group(1).strip() if m else ""

    services, seen = [], set()
    for m in re.finditer(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', h, re.I):
        src, alt = m.group(1).strip(), _clean_text(m.group(2))
        if not src.startswith("upload/") or "iblock" not in src:
            continue
        if src in seen or not alt or "\u043b\u043e\u0433\u043e\u0442\u0438\u043f" in alt.lower():
            continue          # логотипы и дубли не берём
        seen.add(src)
        services.append((alt, src))
    data["services"] = services
    return data


def _extract_tail(h):
    """Сохраняем служебные скрипты, которые подключает родитель:
    jQuery + inputmask + готовый клиент заявок (window.SITE_LEADS)."""
    parts = []
    for pat in (r'<script[^>]*src="[^"]*jquery[^"]*\.js"[^>]*>\s*</script>',
                r'<script[^>]*src="[^"]*inputmask[^"]*"[^>]*>\s*</script>'):
        m = re.search(pat, h, re.I)
        if m:
            parts.append(m.group(0))
    lead = re.search(r"<script>\s*window\.SITE_LEADS\b.*?</script>", h, re.S)
    if lead:
        parts.append(lead.group(0))
    else:  # запасной вариант: не терять то, что положил родитель
        s = re.search(r"<script\b", h)
        b = h.rfind("</body>")
        if s and b > s.start():
            parts.append(h[s.start():b])
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# <head>: SEO + фирменные стили
# ---------------------------------------------------------------------------
def _head(h, cfg, data):
    A, AD = _accent(cfg)
    C = cfg.get("city") or {}
    city = (C.get("prep") or C.get("nom") or "\u041c\u043e\u0441\u043a\u0432\u0435")
    city_nom = (C.get("nom") or "\u041c\u043e\u0441\u043a\u0432\u0430")
    site = (cfg.get("siteUrl") or "").rstrip("/") + "/"
    phone_raw = cfg.get("phoneRaw") or ""
    email = cfg.get("email") or ""
    hours = cfg.get("openingHours") or ""
    company = cfg.get("company") or {}
    h1 = data.get("h1") or "\u0420\u0435\u043c\u043e\u043d\u0442 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele"

    title = h1 if len(h1) > 55 else h1 + " \u2014 \u0432\u044b\u0435\u0437\u0434 \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c"
    desc = ("\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u043f\u043e \u0440\u0435\u043c\u043e\u043d\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele \u0432 " + city
            + " \u0438 \u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u043e\u0439 \u043e\u0431\u043b\u0430\u0441\u0442\u0438. \u0412\u044b\u0435\u0437\u0434 \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c, "
            + "\u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435, \u0437\u0430\u044f\u0432\u043a\u0430 \u043f\u043e \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0443 " + (cfg.get("phonePretty") or "") + ".")
    site_name = "\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u043f\u043e \u0440\u0435\u043c\u043e\u043d\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele"

    # убрать тяжёлые стили/иконки копии шаблона (конфликтуют с нашей вёрсткой)
    h = re.sub(r'<link\b[^>]*href="(?:bitrix|lib)/[^"]*"[^>]*>\s*', "", h, flags=re.I)
    h = re.sub(r'<link\b[^>]*href="favicon\.ico"[^>]*>\s*', "", h, flags=re.I)

    # title
    title_tag = "<title>%s</title>" % _escape(title)
    if re.search(r"<title\b", h, re.I):
        h = re.sub(r"<title\b[^>]*>.*?</title>", lambda m: title_tag, h, count=1, flags=re.S | re.I)
    else:
        h = h.replace("</head>", title_tag + "</head>", 1)

    # description
    desc_tag = '<meta name="description" content="%s">' % _escape(desc)
    if re.search(r'<meta\s+name="description"', h, re.I):
        h = re.sub(r'<meta\s+name="description"[^>]*>', lambda m: desc_tag, h, count=1, flags=re.I)
    elif "</title>" in h:
        h = h.replace("</title>", "</title>\n" + desc_tag, 1)

    # charset
    if not re.search(r"<meta\s+charset", h, re.I):
        h = h.replace("<head>", '<head>\n<meta charset="utf-8">', 1)

    # JSON-LD — только реальные факты из config.json, без рейтингов и отзывов
    ld_data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": company.get("shortName") or site_name,
        "url": site,
        "telephone": phone_raw,
        "email": email,
        "areaServed": {"@type": "City", "name": city_nom},
        "description": desc,
    }
    if hours:
        ld_data["openingHours"] = hours
    if company.get("inn"):
        ld_data["taxID"] = company["inn"]
    ld = '<script type="application/ld+json">%s</script>' % json.dumps(ld_data, ensure_ascii=False)

    og_img = site + "assets/og-default.jpg"
    bundle = "\n".join([
        '<link rel="canonical" href="%s">' % _escape(site),
        '<meta name="robots" content="index,follow">',
        '<meta name="theme-color" content="%s">' % A,
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="ru_RU">',
        '<meta property="og:site_name" content="%s">' % _escape(site_name),
        '<meta property="og:title" content="%s">' % _escape(title),
        '<meta property="og:description" content="%s">' % _escape(desc),
        '<meta property="og:url" content="%s">' % _escape(site),
        '<meta property="og:image" content="%s">' % _escape(og_img),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % _escape(title),
        '<meta name="twitter:description" content="%s">' % _escape(desc),
        '<meta name="twitter:image" content="%s">' % _escape(og_img),
        '<link rel="icon" type="image/png" href="favicon.png">',
        ld,
        '<style id="fe-css">%s</style>' % CSS.replace("__A__", A).replace("__AD__", AD),
    ])
    h = h.replace("</head>", bundle + "\n</head>", 1)
    return h


# ---------------------------------------------------------------------------
# <body>: чистая адаптивная композиция
# ---------------------------------------------------------------------------
def _mk_body(cfg, data):
    A, AD = _accent(cfg)
    C = cfg.get("city") or {}
    city = (C.get("prep") or C.get("nom") or "\u041c\u043e\u0441\u043a\u0432\u0435")
    phone_pretty = cfg.get("phonePretty") or ""
    phone_raw = cfg.get("phoneRaw") or ""
    email = cfg.get("email") or ""
    hours = cfg.get("workHours") or ""
    company = cfg.get("company") or {}
    short = company.get("shortName") or ""
    inn = company.get("inn") or ""
    h1 = data.get("h1") or "\u0420\u0435\u043c\u043e\u043d\u0442 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele"
    hero = data.get("hero") or ""
    services = data.get("services") or []
    if not services:
        services = [(n, "") for n in DEFAULT_SERVICES]

    hero_style = ""
    if hero:
        hero_style = (' style="background-image:linear-gradient(120deg, rgba(27,27,27,.88) 0%, '
                      'rgba(122,0,8,.72) 100%), url(\'' + _escape(hero) + '\')"')

    cards = "\n".join(
        '<a class="fe-card" href="#zayavka">'
        + ('<span class="fe-card__img"><img loading="lazy" src="%s" alt="%s"></span>' % (_escape(src), _escape(name)) if src else "")
        + '<span class="fe-card__t">%s</span></a>' % _escape(name)
        for name, src in services)

    foot_links = "\n".join('<a href="#uslugi">%s</a>' % _escape(n) for n, _s in services[:6])
    if not foot_links:
        foot_links = '<a href="#uslugi">\u0420\u0435\u043c\u043e\u043d\u0442 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele</a>'

    legal_bits = []
    if short:
        legal_bits.append("\u042e\u0440\u043b\u0438\u0446\u043e: " + short)
    if inn:
        legal_bits.append("\u0418\u041d\u041d " + inn)
    legal = ('<p class="legal">%s</p>' % _escape(", ".join(legal_bits))) if legal_bits else ""

    phone_link = ('<a class="fe-phone" href="tel:%s" aria-label="\u041f\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u044c %s">'
                  + PHONE_SVG + '<span class="fe-phone__num">%s</span></a>')

    logo_alt = "\u041b\u043e\u0433\u043e\u0442\u0438\u043f \u2014 \u0440\u0435\u043c\u043e\u043d\u0442 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele"
    logo_header = cfg.get("logo") or "assets/logo.svg"
    logo_footer = cfg.get("logoFooter") or "assets/logo-footer.svg"
    logo_img = '<img style="width: 202px;" src="%s" alt="%s">' % (logo_header, logo_alt)
    logo_foot_img = '<img style="width: 202px;" src="%s" alt="%s">' % (logo_footer, logo_alt)

    consent = ('<label class="fe-consent">'
               '<input type="checkbox" id="%s" name="consent" value="1" required>'
               '<span>\u0421\u043e\u0433\u043b\u0430\u0441\u0435\u043d \u043d\u0430 '
               '<a href="politika.html" target="_blank" rel="noopener">\u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0443 '
               '\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445</a></span></label>')

    def field(label, inp):
        return '<label class="fe-field"><span>%s</span>%s</label>' % (label, inp)

    html = """<header class="fe-header" id="header">
  <div class="fe-wrap fe-header__in">
    <a class="fe-logo" href="index.html" aria-label="\u041d\u0430 \u0433\u043b\u0430\u0432\u043d\u0443\u044e">%LOGO%</a>
    <nav class="fe-nav" id="fe-nav" aria-label="\u041e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u043d\u0430\u0432\u0438\u0433\u0430\u0446\u0438\u044f">
      <a href="#uslugi">\u0423\u0441\u043b\u0443\u0433\u0438</a>
      <a href="#process">\u041a\u0430\u043a \u043c\u044b \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u043c</a>
      <a href="#zayavka">\u041e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443</a>
      <a href="#footer">\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b</a>
    </nav>
    <div class="fe-header__cta">
      %PHONE%
      <button type="button" class="fe-btn fe-btn--accent" data-modal="#callback_popup">\u0417\u0430\u043a\u0430\u0437\u0430\u0442\u044c \u0437\u0432\u043e\u043d\u043e\u043a</button>
      <button type="button" class="fe-burger" aria-label="\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u043c\u0435\u043d\u044e" aria-expanded="false" aria-controls="fe-nav"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>

<section class="fe-hero"%HERO%>
  <div class="fe-wrap">
    <div class="fe-hero__in">
      <p class="fe-hero__kicker">\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u00b7 %CITY% \u0438 \u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u0430\u044f \u043e\u0431\u043b\u0430\u0441\u0442\u044c</p>
      <h1>%H1%</h1>
      <p class="fe-hero__lead">\u0412\u044b\u0435\u0437\u0434 \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c, \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435 \u0438 \u0440\u0435\u043c\u043e\u043d\u0442 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele.</p>
      <div class="fe-hero__cta">
        <button type="button" class="fe-btn fe-btn--accent fe-btn--lg" data-modal="#zayavka_popup">\u0412\u044b\u0437\u0432\u0430\u0442\u044c \u043c\u0430\u0441\u0442\u0435\u0440\u0430</button>
        <a class="fe-btn fe-btn--ghost fe-btn--lg" href="tel:%PHONE_RAW%">\u041f\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u044c: %PHONE_PRETTY%</a>
      </div>
      <ul class="fe-hero__facts">
        <li>\u0412\u044b\u0435\u0437\u0434 \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c</li>
        <li>\u0414\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435</li>
        <li>%HOURS%</li>
      </ul>
    </div>
  </div>
</section>

<section class="fe-sec" id="uslugi">
  <div class="fe-wrap">
    <h2>\u041c\u044b \u0440\u0435\u043c\u043e\u043d\u0442\u0438\u0440\u0443\u0435\u043c \u0442\u0435\u0445\u043d\u0438\u043a\u0443 Miele</h2>
    <p class="fe-sec__sub">\u0412\u044b\u0435\u0437\u0434\u043d\u043e\u0439 \u0440\u0435\u043c\u043e\u043d\u0442 \u0431\u044b\u0442\u043e\u0432\u043e\u0439 \u0438 \u043f\u0440\u043e\u0444\u0435\u0441\u0441\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0439 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele \u0432 %CITY% \u0438 \u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u043e\u0439 \u043e\u0431\u043b\u0430\u0441\u0442\u0438.</p>
    <div class="fe-grid">
%CARDS%
    </div>
  </div>
</section>

<section class="fe-sec fe-sec--soft" id="process">
  <div class="fe-wrap fe-two">
    <div>
      <h2>\u041a\u0430\u043a \u043c\u044b \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u043c</h2>
      <ol class="fe-steps">
        <li><b>\u0417\u0430\u044f\u0432\u043a\u0430.</b> \u041f\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u0435 \u043f\u043e \u043d\u043e\u043c\u0435\u0440\u0443 <a href="tel:%PHONE_RAW%">%PHONE_PRETTY%</a> \u0438\u043b\u0438 \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0444\u043e\u0440\u043c\u0443 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435.</li>
        <li><b>\u0423\u0442\u043e\u0447\u043d\u0435\u043d\u0438\u0435.</b> \u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 \u0443\u0442\u043e\u0447\u043d\u0438\u0442 \u0445\u0430\u0440\u0430\u043a\u0442\u0435\u0440 \u043f\u043e\u043b\u043e\u043c\u043a\u0438 \u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u0442 \u0443\u0434\u043e\u0431\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u0432\u0438\u0437\u0438\u0442\u0430.</li>
        <li><b>\u0412\u044b\u0435\u0437\u0434.</b> \u041c\u0430\u0441\u0442\u0435\u0440 \u043f\u0440\u0438\u0435\u0437\u0436\u0430\u0435\u0442 \u043d\u0430 \u0434\u043e\u043c \u0438 \u043f\u0440\u043e\u0432\u043e\u0434\u0438\u0442 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0443 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435.</li>
        <li><b>\u0421\u043e\u0433\u043b\u0430\u0441\u043e\u0432\u0430\u043d\u0438\u0435.</b> \u0423\u0441\u043b\u043e\u0432\u0438\u044f \u0438 \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0440\u0435\u043c\u043e\u043d\u0442\u0430 \u0441\u043e\u0433\u043b\u0430\u0441\u0443\u044e\u0442\u0441\u044f \u0434\u043e \u043d\u0430\u0447\u0430\u043b\u0430 \u0440\u0430\u0431\u043e\u0442.</li>
        <li><b>\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430.</b> \u041f\u043e\u0441\u043b\u0435 \u0440\u0435\u043c\u043e\u043d\u0442\u0430 \u043c\u0430\u0441\u0442\u0435\u0440 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0435\u0442 \u0440\u0430\u0431\u043e\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 \u043d\u0430 \u043c\u0435\u0441\u0442\u0435.</li>
      </ol>
    </div>
    <div class="fe-note">
      <h2>\u041e \u0441\u0435\u0440\u0432\u0438\u0441\u0435</h2>
      <p>\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u043f\u043e \u0440\u0435\u043c\u043e\u043d\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele \u0432 %CITY% \u0438 \u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u043e\u0439 \u043e\u0431\u043b\u0430\u0441\u0442\u0438. \u0420\u0430\u0431\u043e\u0442\u0430\u0435\u043c \u0441 \u0432\u044b\u0435\u0437\u0434\u043e\u043c \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c: \u0441\u0442\u0438\u0440\u0430\u043b\u044c\u043d\u044b\u0435 \u0438 \u0441\u0443\u0448\u0438\u043b\u044c\u043d\u044b\u0435 \u043c\u0430\u0448\u0438\u043d\u044b, \u0445\u043e\u043b\u043e\u0434\u0438\u043b\u044c\u043d\u0438\u043a\u0438, \u043a\u043e\u0444\u0435\u043c\u0430\u0448\u0438\u043d\u044b, \u043f\u043e\u0441\u0443\u0434\u043e\u043c\u043e\u0435\u0447\u043d\u044b\u0435 \u0438 \u0432\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0435\u043c\u0430\u044f \u0442\u0435\u0445\u043d\u0438\u043a\u0430 Miele.</p>
      <p>\u0414\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430 \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442\u0441\u044f \u043d\u0430 \u043c\u0435\u0441\u0442\u0435, \u043f\u0440\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u0438 \u0434\u0435\u0442\u0430\u043b\u0438 \u0438 \u0441\u0440\u043e\u043a\u0438 \u0441\u043e\u0433\u043b\u0430\u0441\u0443\u044e\u0442\u0441\u044f \u0437\u0430\u0440\u0430\u043d\u0435\u0435.</p>
    </div>
  </div>
</section>

<section class="fe-sec fe-formsec" id="zayavka">
  <div class="fe-wrap fe-formsec__in">
    <div class="fe-formsec__text">
      <h2>\u041d\u0443\u0436\u043d\u0430 \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u0446\u0438\u044f \u0441\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442\u0430?</h2>
      <p>\u041f\u043e\u0437\u0432\u043e\u043d\u0438\u0442\u0435 \u043f\u043e \u043d\u043e\u043c\u0435\u0440\u0443 <a href="tel:%PHONE_RAW%">%PHONE_PRETTY%</a> \u0438\u043b\u0438 \u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0437\u0430\u044f\u0432\u043a\u0443 \u2014 \u043c\u044b \u043f\u0435\u0440\u0435\u0437\u0432\u043e\u043d\u0438\u043c \u0438 \u0443\u0442\u043e\u0447\u043d\u0438\u043c \u0434\u0435\u0442\u0430\u043b\u0438.</p>
      <p class="fe-formsec__note">\u041e\u0442\u043f\u0440\u0430\u0432\u043b\u044f\u044f \u0444\u043e\u0440\u043c\u0443, \u0432\u044b \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0430\u0435\u0442\u0435 \u0441\u043e\u0433\u043b\u0430\u0441\u0438\u0435 \u043d\u0430 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0443 \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0445 \u0434\u0430\u043d\u043d\u044b\u0445.</p>
    </div>
    <form id="form_vopros_expert" class="feedback fe-form" method="post">
      <div class="title">\u041e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443</div>
      %F_NAME%
      %F_PHONE%
      %F_MSG%
      %CONSENT_EXPERT%
      <div id="garant_error_expert" class="fe-error" role="alert"></div>
      <button type="submit" class="fe-btn fe-btn--accent fe-btn--lg">\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443</button>
    </form>
  </div>
</section>

<footer class="fe-footer" id="footer">
  <div class="fe-wrap fe-footer__top">
    <div class="fe-footer__col">
      %LOGO_FOOT%
      <p class="fe-footer__about">\u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u043f\u043e \u0440\u0435\u043c\u043e\u043d\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele \u0432 %CITY% \u0438 \u041c\u043e\u0441\u043a\u043e\u0432\u0441\u043a\u043e\u0439 \u043e\u0431\u043b\u0430\u0441\u0442\u0438. \u0412\u044b\u0435\u0437\u0434 \u043c\u0430\u0441\u0442\u0435\u0440\u0430 \u043d\u0430 \u0434\u043e\u043c.</p>
    </div>
    <div class="fe-footer__col">
      <h3>\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b</h3>
      <p><a href="tel:%PHONE_RAW%">%PHONE_PRETTY%</a></p>
      <p><a href="mailto:%EMAIL%">%EMAIL%</a></p>
      <p>%HOURS%</p>
    </div>
    <div class="fe-footer__col">
      <h3>\u0423\u0441\u043b\u0443\u0433\u0438</h3>
      <nav>%FOOT_LINKS%</nav>
    </div>
    <div class="fe-footer__col">
      <h3>\u0418\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f</h3>
      <nav>
        <a href="politika.html">\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 \u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438</a>
        <a href="soglasie.html">\u0421\u043e\u0433\u043b\u0430\u0441\u0438\u0435 \u043d\u0430 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0443 \u041f\u0414</a>
        <a href="requisites.html">\u042e\u0440\u0438\u0434\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f</a>
      </nav>
    </div>
  </div>
  <div class="fe-footer__bottom">
    <div class="fe-wrap">
      <p>\u00a9 %YEAR% \u0421\u0435\u0440\u0432\u0438\u0441\u043d\u044b\u0439 \u0446\u0435\u043d\u0442\u0440 \u043f\u043e \u0440\u0435\u043c\u043e\u043d\u0442\u0443 \u0442\u0435\u0445\u043d\u0438\u043a\u0438 Miele, %CITY%</p>
      %LEGAL%
    </div>
  </div>
</footer>

<div class="fe-modal" id="callback_popup" hidden>
  <div class="fe-modal__ov" data-close></div>
  <div class="fe-modal__box" role="dialog" aria-modal="true" aria-labelledby="fe-cb-title">
    <button type="button" class="fe-modal__x" data-close aria-label="\u0417\u0430\u043a\u0440\u044b\u0442\u044c">\u00d7</button>
    <form id="form_callback_popup" class="feedback fe-form" method="post">
      <div class="title" id="fe-cb-title">\u041e\u0431\u0440\u0430\u0442\u043d\u044b\u0439 \u0437\u0432\u043e\u043d\u043e\u043a</div>
      <p class="fe-modal__sub">\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0442\u0435\u043b\u0435\u0444\u043e\u043d \u2014 \u043f\u0435\u0440\u0435\u0437\u0432\u043e\u043d\u0438\u043c \u0438 \u0443\u0442\u043e\u0447\u043d\u0438\u043c \u0434\u0435\u0442\u0430\u043b\u0438.</p>
      %F_NAME%
      %F_PHONE%
      %CONSENT_CALLBACK%
      <div id="garant_error_callback" class="fe-error" role="alert"></div>
      <button type="submit" class="fe-btn fe-btn--accent fe-btn--lg">\u041f\u0435\u0440\u0435\u0437\u0432\u043e\u043d\u0438\u0442\u0435 \u043c\u043d\u0435</button>
    </form>
  </div>
</div>

<div class="fe-modal" id="zayavka_popup" hidden>
  <div class="fe-modal__ov" data-close></div>
  <div class="fe-modal__box" role="dialog" aria-modal="true" aria-labelledby="fe-za-title">
    <button type="button" class="fe-modal__x" data-close aria-label="\u0417\u0430\u043a\u0440\u044b\u0442\u044c">\u00d7</button>
    <form id="form_zayvka_popup" class="feedback fe-form" method="post">
      <div class="title" id="fe-za-title">\u0417\u0430\u044f\u0432\u043a\u0430 \u043d\u0430 \u0440\u0435\u043c\u043e\u043d\u0442</div>
      %F_NAME%
      %F_PHONE%
      %F_MSG%
      %CONSENT_ZAYVKA%
      <div id="garant_error_zayavka" class="fe-error" role="alert"></div>
      <button type="submit" class="fe-btn fe-btn--accent fe-btn--lg">\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443</button>
    </form>
  </div>
</div>"""

    import datetime
    year = datetime.date.today().year

    repl = {
        "%LOGO%": logo_img,
        "%LOGO_FOOT%": logo_foot_img,
        "%PHONE%": phone_link % (phone_raw, phone_pretty, phone_pretty),
        "%HERO%": hero_style,
        "%CITY%": _escape(city),
        "%H1%": _escape(h1),
        "%HOURS%": _escape(hours),
        "%PHONE_RAW%": _escape(phone_raw),
        "%PHONE_PRETTY%": _escape(phone_pretty),
        "%EMAIL%": _escape(email),
        "%CARDS%": cards,
        "%FOOT_LINKS%": foot_links,
        "%LEGAL%": legal,
        "%YEAR%": str(year),
        "%F_NAME%": field("\u0412\u0430\u0448\u0435 \u0438\u043c\u044f",
                          '<input type="text" name="form_name" placeholder="\u0412\u0430\u0448\u0435 \u0438\u043c\u044f" maxlength="50" autocomplete="name">'),
        "%F_PHONE%": field("\u0422\u0435\u043b\u0435\u0444\u043e\u043d *",
                           '<input type="tel" name="form_phone" class="inputmask" placeholder="+7 (___) ___-__-__" required autocomplete="tel">'),
        "%F_MSG%": field("\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439",
                         '<textarea name="form_message" rows="3" maxlength="500" placeholder="\u041e\u043f\u0438\u0448\u0438\u0442\u0435 \u043f\u0440\u043e\u0431\u043b\u0435\u043c\u0443 \u0441 \u0442\u0435\u0445\u043d\u0438\u043a\u043e\u0439"></textarea>'),
        "%CONSENT_EXPERT%": consent % "garant_ch_expert",
        "%CONSENT_CALLBACK%": consent % "garant_ch_callback",
        "%CONSENT_ZAYVKA%": consent % "garant_ch_zayvka",
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


# ---------------------------------------------------------------------------
# публичный API
# ---------------------------------------------------------------------------
def improve_html(h, cfg):
    """Главная точка входа. Принимает собранный build.py HTML и config.json,
    возвращает доработанный HTML (не бросает исключений на понятных данных)."""
    if not h or "<body" not in h.lower():
        return h
    cfg = cfg or {}
    try:
        data = _parse(h, cfg)
        tail = _extract_tail(h)
        inner = _mk_body(cfg, data)
        new_body = ("<body>\n" + inner + "\n" + tail
                    + "\n<script>\n" + JS + "\n</script>\n</body>")
        h2 = re.sub(r"<body[^>]*>.*?</body>",
                    lambda m: new_body, h, count=1, flags=re.S | re.I)
        if h2 == h:
            return h
        h2 = _head(h2, cfg, data)
        return h2
    except Exception:
        return h


def write_assets(out_dir, cfg=None):
    """Опциональный хелпер: выгрузить стили и скрипт отдельными файлами.
    По умолчанию improve_html встраивает их inline и вызов не нужен."""
    a, ad = _accent(cfg or {})
    d = os.path.join(out_dir, "assets")
    os.makedirs(d, exist_ok=True)
    css_path = os.path.join(d, "frontend.css")
    js_path = os.path.join(d, "frontend.js")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(CSS.replace("__A__", a).replace("__AD__", ad))
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(JS)
    return css_path, js_path
