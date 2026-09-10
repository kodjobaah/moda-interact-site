# Moda Interact static website

This bundle contains a simple static company website for Moda Interact Ltd.

## Live site

- Deployed site: https://www.modainteract.com/
- Product walkthrough: https://www.modainteract.com/usage-interactions.mp4



## Internationalisation

The public site supports the same 20 locales as the Moda Interact merchant product. On first visit it selects the first supported browser language, falls back to English, and provides a language selector that persists the visitor's explicit choice across pages.

Translation source files and maintenance instructions live in [`i18n/README.md`](i18n/README.md).

Validate the locale catalogues and generated browser bundle with:

```bash
python3 i18n/build-translations.py --check
node --check i18n/translations.js
node --check i18n/site-i18n.js
node i18n/check-locale-resolution.js
```
