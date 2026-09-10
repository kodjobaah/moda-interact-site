(function () {
  'use strict';

  const catalog = window.MODA_TRANSLATIONS;
  if (!catalog || !catalog.messages || !catalog.languages) return;

  const STORAGE_KEY = 'moda-interact-language';
  const DEFAULT_LOCALE = 'en';
  const SUPPORTED = new Set(Object.keys(catalog.languages));
  const originalText = new WeakMap();

  function normaliseLocale(value) {
    if (!value) return null;
    const raw = String(value).replace(/_/g, '-').trim();
    if (!raw) return null;

    const exact = [...SUPPORTED].find((locale) => locale.toLowerCase() === raw.toLowerCase());
    if (exact) return exact;

    const lower = raw.toLowerCase();
    if (lower === 'no' || lower.startsWith('no-') || lower.startsWith('nb-')) return 'nb';
    if (lower === 'pt-br' || lower.startsWith('pt-br-')) return 'pt-BR';
    if (lower === 'pt-pt' || lower.startsWith('pt-pt-')) return 'pt-PT';
    if (lower === 'pt') return 'pt-PT';
    if (lower === 'zh-hant' || lower.startsWith('zh-tw') || lower.startsWith('zh-hk') || lower.startsWith('zh-mo')) return 'zh-Hant';
    if (lower === 'zh-hans' || lower.startsWith('zh-cn') || lower.startsWith('zh-sg') || lower.startsWith('zh-my')) return 'zh-Hans';
    if (lower === 'zh') return 'zh-Hans';

    const base = lower.split('-')[0];
    const baseMatch = [...SUPPORTED].find((locale) => locale.toLowerCase() === base);
    return baseMatch || null;
  }

  function languageFromUrl() {
    try {
      return normaliseLocale(new URL(window.location.href).searchParams.get('lang'));
    } catch (_) {
      return null;
    }
  }

  function languageFromStorage() {
    try {
      return normaliseLocale(window.localStorage.getItem(STORAGE_KEY));
    } catch (_) {
      return null;
    }
  }

  function languageFromBrowser() {
    const candidates = Array.isArray(navigator.languages) && navigator.languages.length
      ? navigator.languages
      : [navigator.language];
    for (const candidate of candidates) {
      const locale = normaliseLocale(candidate);
      if (locale) return locale;
    }
    return null;
  }

  function resolveInitialLocale() {
    return languageFromUrl() || languageFromStorage() || languageFromBrowser() || DEFAULT_LOCALE;
  }

  function translatePattern(locale, source) {
    const patterns = (catalog.patterns && catalog.patterns[locale]) || (catalog.patterns && catalog.patterns[DEFAULT_LOCALE]) || {};
    const rules = [
      [/^(\d+) conversations$/, 'conversations'],
      [/^(\d+) monthly recovery conversations\.$/, 'monthlyRecovery'],
      [/^(\d+) lifetime conversations$/, 'lifetimeRecovery'],
      [/^£(\d+) pack$/, 'pack'],
    ];
    for (const [regex, key] of rules) {
      const match = source.match(regex);
      if (match && patterns[key]) return patterns[key].replace('{n}', match[1]);
    }
    if (source === '/month' && patterns.perMonth) return patterns.perMonth;
    if (source === 'recovery conversations every month' && patterns.recoveryEveryMonth) return patterns.recoveryEveryMonth;
    return null;
  }

  function translate(locale, source) {
    const localeMessages = catalog.messages[locale] || {};
    const exact = localeMessages[source] || catalog.messages[DEFAULT_LOCALE][source];
    if (exact) return exact;
    return translatePattern(locale, source) || source;
  }

  function translateInterface(locale, key) {
    const source = catalog.interface[DEFAULT_LOCALE][key];
    return (catalog.interface[locale] && catalog.interface[locale][key]) || source || key;
  }

  function normaliseSource(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function replaceTextNode(node, locale) {
    if (!originalText.has(node)) originalText.set(node, node.nodeValue);
    const original = originalText.get(node);
    const source = normaliseSource(original);
    if (!source) return;
    const translated = translate(locale, source);

    const leading = (original.match(/^\s*/) || [''])[0];
    const trailing = (original.match(/\s*$/) || [''])[0];
    node.nodeValue = `${leading}${translated}${trailing}`;
  }

  function translateTextNodes(locale) {
    const walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'CODE', 'PRE'].includes(parent.tagName)) return NodeFilter.FILTER_REJECT;
        if (parent.closest('[data-i18n-ignore]')) return NodeFilter.FILTER_REJECT;
        return normaliseSource(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });

    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => replaceTextNode(node, locale));
  }

  function translateAttributes(locale) {
    document.querySelectorAll('meta[name="description"], meta[property="og:title"], meta[property="og:description"]').forEach((element) => {
      const english = element.dataset.i18nSource || normaliseSource(element.getAttribute('content'));
      if (!element.dataset.i18nSource) element.dataset.i18nSource = english;
      element.setAttribute('content', translate(locale, english));
    });

    document.querySelectorAll('[alt]').forEach((element) => {
      const english = element.dataset.i18nAltSource || normaliseSource(element.getAttribute('alt'));
      if (!english) return;
      if (!element.dataset.i18nAltSource) element.dataset.i18nAltSource = english;
      element.setAttribute('alt', translate(locale, english));
    });
  }

  function translateTitle(locale) {
    const title = document.querySelector('title');
    if (!title) return;
    const english = title.dataset.i18nSource || normaliseSource(title.textContent);
    if (!title.dataset.i18nSource) title.dataset.i18nSource = english;
    title.textContent = translate(locale, english);
  }

  function appendLanguageToHref(href, locale) {
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('javascript:')) return href;
    try {
      const url = new URL(href, window.location.href);
      if (url.origin !== window.location.origin && window.location.protocol !== 'file:') return href;
      if (window.location.protocol === 'file:' && url.protocol !== 'file:') return href;
      url.searchParams.set('lang', locale);
      if (window.location.protocol === 'file:') {
        return `${url.pathname.split('/').pop()}${url.search}${url.hash}`;
      }
      return `${url.pathname}${url.search}${url.hash}`;
    } catch (_) {
      return href;
    }
  }

  function updateInternalLinks(locale) {
    document.querySelectorAll('a[href]').forEach((anchor) => {
      if (anchor.closest('[data-i18n-ignore]')) return;
      const original = anchor.dataset.i18nHref || anchor.getAttribute('href');
      if (!anchor.dataset.i18nHref) anchor.dataset.i18nHref = original;
      anchor.setAttribute('href', appendLanguageToHref(original, locale));
    });
  }

  function updateLegalNotice(locale) {
    const notice = document.querySelector('[data-legal-language-notice]');
    if (!notice) return;
    if (locale === DEFAULT_LOCALE) {
      notice.hidden = true;
      notice.textContent = '';
      return;
    }
    notice.textContent = translateInterface(locale, 'legalNotice');
    notice.hidden = false;
  }

  function updateSelector(locale) {
    const button = document.querySelector('[data-language-button]');
    if (!button) return;
    const language = catalog.languages[locale];
    const label = translateInterface(locale, 'language');
    button.setAttribute('aria-label', `${label}: ${language.nativeName}`);
    button.querySelector('[data-language-current]').textContent = language.nativeName;
    document.querySelectorAll('[data-language-option]').forEach((option) => {
      const selected = option.dataset.languageOption === locale;
      option.setAttribute('aria-checked', selected ? 'true' : 'false');
      option.classList.toggle('is-selected', selected);
    });
  }

  function applyLocale(locale) {
    const resolved = normaliseLocale(locale) || DEFAULT_LOCALE;
    document.documentElement.lang = resolved;
    document.documentElement.dir = 'ltr';


    translateTitle(resolved);
    translateTextNodes(resolved);
    translateAttributes(resolved);
    updateLegalNotice(resolved);
    updateSelector(resolved);
    updateInternalLinks(resolved);
    document.documentElement.dataset.modaLocale = resolved;
    window.dispatchEvent(new CustomEvent('moda:language-changed', { detail: { locale: resolved } }));
    return resolved;
  }

  function setLocale(locale, persist) {
    const resolved = normaliseLocale(locale) || DEFAULT_LOCALE;
    if (persist) {
      try { window.localStorage.setItem(STORAGE_KEY, resolved); } catch (_) {}
      try {
        const url = new URL(window.location.href);
        url.searchParams.set('lang', resolved);
        window.history.replaceState({}, '', url);
      } catch (_) {}
    }
    applyLocale(resolved);
    return resolved;
  }

  function createLanguageSelector(locale) {
    const nav = document.querySelector('.nav-links');
    if (!nav || nav.querySelector('[data-language-switcher]')) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'language-switcher';
    wrapper.dataset.languageSwitcher = '';
    wrapper.dataset.i18nIgnore = '';

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'language-button';
    button.dataset.languageButton = '';
    button.setAttribute('aria-haspopup', 'menu');
    button.setAttribute('aria-expanded', 'false');
    button.innerHTML = '<span aria-hidden="true">🌐</span><span data-language-current></span><span class="language-chevron" aria-hidden="true">▾</span>';

    const menu = document.createElement('div');
    menu.className = 'language-menu';
    menu.setAttribute('role', 'menu');
    menu.hidden = true;

    Object.entries(catalog.languages).forEach(([code, language]) => {
      const option = document.createElement('button');
      option.type = 'button';
      option.className = 'language-option';
      option.dataset.languageOption = code;
      option.setAttribute('role', 'menuitemradio');
      option.innerHTML = `<span class="language-option-check" aria-hidden="true">✓</span><span>${language.nativeName}</span>`;
      option.addEventListener('click', () => {
        setLocale(code, true);
        menu.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      });
      menu.appendChild(option);
    });

    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', open ? 'false' : 'true');
      menu.hidden = open;
      if (!open) {
        const selected = menu.querySelector('.is-selected') || menu.querySelector('.language-option');
        if (selected) selected.focus();
      }
    });

    wrapper.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        menu.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      }
    });

    document.addEventListener('click', (event) => {
      if (!wrapper.contains(event.target)) {
        menu.hidden = true;
        button.setAttribute('aria-expanded', 'false');
      }
    });

    wrapper.appendChild(button);
    wrapper.appendChild(menu);

    const adminLink = [...nav.querySelectorAll('a')].find((anchor) => normaliseSource(anchor.textContent) === 'UI - Admin');
    nav.insertBefore(wrapper, adminLink || null);
    updateSelector(locale);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const initial = resolveInitialLocale();
    createLanguageSelector(initial);
    applyLocale(initial);
  });

  window.ModaI18n = {
    setLocale,
    getLocale: () => document.documentElement.dataset.modaLocale || DEFAULT_LOCALE,
    supportedLocales: () => Object.keys(catalog.languages),
    normaliseLocale
  };
})();
