# Public-site internationalisation

Moda Interact's public static site uses the same 20-language set as the merchant product.
English HTML remains the readable source/fallback; JavaScript replaces translatable text at runtime.
No framework, network translation service, or LaTeX-to-HTML conversion is required.

## Supported locales

`cs`, `da`, `de`, `en`, `es`, `fi`, `fr`, `it`, `ja`, `ko`, `nb`, `nl`, `pl`, `pt-BR`, `pt-PT`, `sv`, `th`, `tr`, `zh-Hans`, `zh-Hant`.

## Resolution order

1. Explicit `?lang=<locale>` URL parameter.
2. A visitor's previously selected language stored in `localStorage`.
3. The first supported browser language from `navigator.languages` / `navigator.language`.
4. English fallback.

Browser aliases are normalised, including `no-* -> nb`, `pt-BR`, `pt-PT`, `zh-CN/zh-SG -> zh-Hans`, and `zh-TW/zh-HK/zh-MO -> zh-Hant`.

## Files

- `site-i18n.js` — browser detection, language selector, persistence, text/meta/alt translation and internal-link propagation.
- `<locale>.json` — one translation catalogue per supported locale. Keys are exact English source strings.
- `translations.js` — generated browser bundle; do not edit it directly.
- `build-translations.py` — validates catalogue parity and rebuilds/checks the browser bundle.

## Updating copy

The English HTML is the source of truth. If visible English copy changes, add the new exact English source string to every locale JSON file, then run:

```bash
python3 i18n/build-translations.py
python3 i18n/build-translations.py --check
node --check i18n/translations.js
node --check i18n/site-i18n.js
node i18n/check-locale-resolution.js
```

The builder fails if a locale has missing/extra keys or if `--check` finds that the generated bundle is stale.

## Local testing

The generated catalogue is JavaScript rather than runtime-fetched JSON so the language selector also works with a local `file://` preview, for example:

```bash
open index.html
open "file://$(pwd)/pricing.html?lang=fr"
```

On a deployed site, URLs such as `pricing.html?lang=pt-BR` directly select a locale. A manual selector choice is remembered across pages.

## Legal pages

Privacy and Terms are localised for usability. Non-English versions display a notice that the translation is provided for convenience and that the English version governs in the event of conflict or inconsistency.

Translations should be reviewed by a native speaker before treating marketing wording as final. Legal translations should receive appropriate professional/legal review before relying on them in a regulated or contractual context.
