#!/usr/bin/env node
'use strict';

const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = __dirname;

const context = {
  window: {
    location: { href: 'https://www.modainteract.com/', protocol: 'https:', origin: 'https://www.modainteract.com' },
    localStorage: { getItem: () => null, setItem: () => {} },
    dispatchEvent: () => {},
  },
  document: {
    addEventListener: () => {},
    documentElement: { dataset: {} },
  },
  navigator: { languages: ['en-GB'], language: 'en-GB' },
  URL,
  console,
};
context.window.window = context.window;
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root, 'translations.js'), 'utf8'), context);
vm.runInContext(fs.readFileSync(path.join(root, 'site-i18n.js'), 'utf8'), context);

const normalise = context.window.ModaI18n.normaliseLocale;
const cases = new Map([
  ['fr-CA', 'fr'],
  ['de-AT', 'de'],
  ['pt-BR', 'pt-BR'],
  ['pt-PT', 'pt-PT'],
  ['pt', 'pt-PT'],
  ['no-NO', 'nb'],
  ['nb-NO', 'nb'],
  ['zh-CN', 'zh-Hans'],
  ['zh-SG', 'zh-Hans'],
  ['zh-TW', 'zh-Hant'],
  ['zh-HK', 'zh-Hant'],
  ['ja-JP', 'ja'],
  ['ar-SA', null],
]);

let failures = 0;
for (const [input, expected] of cases) {
  const actual = normalise(input);
  if (actual !== expected) {
    console.error(`${input}: expected ${expected}, got ${actual}`);
    failures += 1;
  }
}

if (failures) process.exit(1);
console.log(`Locale resolution checks passed: ${cases.size} cases`);
