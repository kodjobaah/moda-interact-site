#!/usr/bin/env python3
"""Build browser-safe translations.js from the 20 canonical locale JSON files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCALES = [
    "cs", "da", "de", "en", "es", "fi", "fr", "it", "ja", "ko",
    "nb", "nl", "pl", "pt-BR", "pt-PT", "sv", "th", "tr", "zh-Hans", "zh-Hant",
]

LANGUAGES = {
    "cs": {"nativeName": "Čeština"},
    "da": {"nativeName": "Dansk"},
    "de": {"nativeName": "Deutsch"},
    "en": {"nativeName": "English"},
    "es": {"nativeName": "Español"},
    "fi": {"nativeName": "Suomi"},
    "fr": {"nativeName": "Français"},
    "it": {"nativeName": "Italiano"},
    "ja": {"nativeName": "日本語"},
    "ko": {"nativeName": "한국어"},
    "nb": {"nativeName": "Norsk bokmål"},
    "nl": {"nativeName": "Nederlands"},
    "pl": {"nativeName": "Polski"},
    "pt-BR": {"nativeName": "Português (Brasil)"},
    "pt-PT": {"nativeName": "Português (Portugal)"},
    "sv": {"nativeName": "Svenska"},
    "th": {"nativeName": "ไทย"},
    "tr": {"nativeName": "Türkçe"},
    "zh-Hans": {"nativeName": "简体中文"},
    "zh-Hant": {"nativeName": "繁體中文"},
}

INTERFACE = {
    "en": {"language": "Language", "legalNotice": "This translation is provided for convenience. If there is any conflict or inconsistency, the English version governs."},
    "cs": {"language": "Jazyk", "legalNotice": "Tento překlad je poskytován pro usnadnění. V případě rozporu nebo nesrovnalosti je rozhodující anglická verze."},
    "da": {"language": "Sprog", "legalNotice": "Denne oversættelse er kun til orientering. Hvis der er en konflikt eller uoverensstemmelse, er den engelske version gældende."},
    "de": {"language": "Sprache", "legalNotice": "Diese Übersetzung wird zur Vereinfachung bereitgestellt. Bei Widersprüchen oder Abweichungen ist die englische Fassung maßgeblich."},
    "es": {"language": "Idioma", "legalNotice": "Esta traducción se proporciona por comodidad. Si existe algún conflicto o discrepancia, prevalece la versión en inglés."},
    "fi": {"language": "Kieli", "legalNotice": "Tämä käännös tarjotaan käyttömukavuuden vuoksi. Jos versioiden välillä on ristiriitaa tai epäjohdonmukaisuutta, englanninkielinen versio on määräävä."},
    "fr": {"language": "Langue", "legalNotice": "Cette traduction est fournie à titre de commodité. En cas de conflit ou d'incohérence, la version anglaise prévaut."},
    "it": {"language": "Lingua", "legalNotice": "Questa traduzione è fornita per comodità. In caso di conflitto o incongruenza, prevale la versione inglese."},
    "ja": {"language": "言語", "legalNotice": "この翻訳は便宜のために提供されています。内容に矛盾または不一致がある場合は、英語版が優先されます。"},
    "ko": {"language": "언어", "legalNotice": "이 번역은 편의를 위해 제공됩니다. 내용에 충돌이나 불일치가 있는 경우 영어 버전이 우선합니다."},
    "nb": {"language": "Språk", "legalNotice": "Denne oversettelsen tilbys for enkelhets skyld. Ved konflikt eller uoverensstemmelse er den engelske versjonen gjeldende."},
    "nl": {"language": "Taal", "legalNotice": "Deze vertaling wordt voor het gemak aangeboden. Bij een conflict of inconsistentie is de Engelse versie leidend."},
    "pl": {"language": "Język", "legalNotice": "To tłumaczenie udostępniono dla wygody. W przypadku sprzeczności lub rozbieżności rozstrzygająca jest wersja angielska."},
    "pt-BR": {"language": "Idioma", "legalNotice": "Esta tradução é fornecida por conveniência. Em caso de conflito ou inconsistência, prevalece a versão em inglês."},
    "pt-PT": {"language": "Idioma", "legalNotice": "Esta tradução é disponibilizada por conveniência. Em caso de conflito ou inconsistência, prevalece a versão em inglês."},
    "sv": {"language": "Språk", "legalNotice": "Denna översättning tillhandahålls för bekvämlighet. Vid konflikt eller inkonsekvens gäller den engelska versionen."},
    "th": {"language": "ภาษา", "legalNotice": "คำแปลนี้จัดทำขึ้นเพื่อความสะดวก หากมีความขัดแย้งหรือความไม่สอดคล้องใด ๆ ให้ยึดฉบับภาษาอังกฤษเป็นหลัก"},
    "tr": {"language": "Dil", "legalNotice": "Bu çeviri kolaylık sağlamak amacıyla sunulmuştur. Herhangi bir çelişki veya tutarsızlık olması durumunda İngilizce sürüm geçerlidir."},
    "zh-Hans": {"language": "语言", "legalNotice": "本翻译仅为方便阅读而提供。如有任何冲突或不一致，以英文版本为准。"},
    "zh-Hant": {"language": "語言", "legalNotice": "本翻譯僅為方便閱讀而提供。如有任何衝突或不一致，以英文版本為準。"},
}

PATTERNS = {
    "en": {"conversations": "{n} conversations", "monthlyRecovery": "{n} monthly recovery conversations.", "lifetimeRecovery": "{n} lifetime conversations", "pack": "£{n} pack", "perMonth": "/month", "recoveryEveryMonth": "recovery conversations every month"},
    "cs": {"conversations": "{n} konverzací", "monthlyRecovery": "{n} konverzací pro obnovu měsíčně.", "lifetimeRecovery": "{n} doživotních konverzací", "pack": "Balíček za £{n}", "perMonth": "/měsíc", "recoveryEveryMonth": "konverzací pro obnovu za měsíc"},
    "da": {"conversations": "{n} samtaler", "monthlyRecovery": "{n} recovery-samtaler om måneden.", "lifetimeRecovery": "{n} livstidssamtaler", "pack": "£{n}-pakke", "perMonth": "/måned", "recoveryEveryMonth": "recovery-samtaler hver måned"},
    "de": {"conversations": "{n} Gespräche", "monthlyRecovery": "{n} Recovery-Gespräche pro Monat.", "lifetimeRecovery": "{n} lebenslange Gespräche", "pack": "£{n}-Paket", "perMonth": "/Monat", "recoveryEveryMonth": "Recovery-Gespräche pro Monat"},
    "es": {"conversations": "{n} conversaciones", "monthlyRecovery": "{n} conversaciones de recuperación al mes.", "lifetimeRecovery": "{n} conversaciones de por vida", "pack": "Paquete de £{n}", "perMonth": "/mes", "recoveryEveryMonth": "conversaciones de recuperación al mes"},
    "fi": {"conversations": "{n} keskustelua", "monthlyRecovery": "{n} palautuskeskustelua kuukaudessa.", "lifetimeRecovery": "{n} elinikäistä keskustelua", "pack": "£{n} lisäpaketti", "perMonth": "/kuukausi", "recoveryEveryMonth": "palautuskeskustelua kuukaudessa"},
    "fr": {"conversations": "{n} conversations", "monthlyRecovery": "{n} conversations de récupération par mois.", "lifetimeRecovery": "{n} conversations à vie", "pack": "Pack de £{n}", "perMonth": "/mois", "recoveryEveryMonth": "conversations de récupération chaque mois"},
    "it": {"conversations": "{n} conversazioni", "monthlyRecovery": "{n} conversazioni di recupero al mese.", "lifetimeRecovery": "{n} conversazioni a vita", "pack": "Pacchetto da £{n}", "perMonth": "/mese", "recoveryEveryMonth": "conversazioni di recupero ogni mese"},
    "ja": {"conversations": "{n}回の会話", "monthlyRecovery": "月{n}回のリカバリー会話。", "lifetimeRecovery": "生涯{n}回の会話", "pack": "£{n}パック", "perMonth": "/月", "recoveryEveryMonth": "毎月のリカバリー会話"},
    "ko": {"conversations": "대화 {n}회", "monthlyRecovery": "월간 복구 대화 {n}회.", "lifetimeRecovery": "평생 대화 {n}회", "pack": "£{n} 패키지", "perMonth": "/월", "recoveryEveryMonth": "월간 복구 대화"},
    "nb": {"conversations": "{n} samtaler", "monthlyRecovery": "{n} recovery-samtaler per måned.", "lifetimeRecovery": "{n} livstidssamtaler", "pack": "£{n}-pakke", "perMonth": "/måned", "recoveryEveryMonth": "recovery-samtaler hver måned"},
    "nl": {"conversations": "{n} gesprekken", "monthlyRecovery": "{n} herstelgesprekken per maand.", "lifetimeRecovery": "{n} levenslange gesprekken", "pack": "£{n}-pakket", "perMonth": "/maand", "recoveryEveryMonth": "herstelgesprekken per maand"},
    "pl": {"conversations": "{n} rozmów", "monthlyRecovery": "{n} rozmów odzyskujących miesięcznie.", "lifetimeRecovery": "{n} dożywotnich rozmów", "pack": "Pakiet £{n}", "perMonth": "/miesiąc", "recoveryEveryMonth": "rozmów odzyskujących miesięcznie"},
    "pt-BR": {"conversations": "{n} conversas", "monthlyRecovery": "{n} conversas de recuperação por mês.", "lifetimeRecovery": "{n} conversas vitalícias", "pack": "Pacote de £{n}", "perMonth": "/mês", "recoveryEveryMonth": "conversas de recuperação por mês"},
    "pt-PT": {"conversations": "{n} conversas", "monthlyRecovery": "{n} conversas de recuperação por mês.", "lifetimeRecovery": "{n} conversas vitalícias", "pack": "Pacote de £{n}", "perMonth": "/mês", "recoveryEveryMonth": "conversas de recuperação por mês"},
    "sv": {"conversations": "{n} konversationer", "monthlyRecovery": "{n} recoverykonversationer per månad.", "lifetimeRecovery": "{n} livstidskonversationer", "pack": "£{n}-paket", "perMonth": "/månad", "recoveryEveryMonth": "recoverykonversationer varje månad"},
    "th": {"conversations": "{n} บทสนทนา", "monthlyRecovery": "{n} บทสนทนากู้คืนต่อเดือน", "lifetimeRecovery": "{n} บทสนทนาตลอดอายุการใช้งาน", "pack": "แพ็ก £{n}", "perMonth": "/เดือน", "recoveryEveryMonth": "บทสนทนากู้คืนต่อเดือน"},
    "tr": {"conversations": "{n} görüşme", "monthlyRecovery": "Aylık {n} kurtarma görüşmesi.", "lifetimeRecovery": "{n} ömür boyu görüşme", "pack": "£{n} paket", "perMonth": "/ay", "recoveryEveryMonth": "aylık kurtarma görüşmesi"},
    "zh-Hans": {"conversations": "{n} 次对话", "monthlyRecovery": "每月 {n} 次挽回对话。", "lifetimeRecovery": "{n} 次终身对话", "pack": "£{n} 套餐", "perMonth": "/月", "recoveryEveryMonth": "每月挽回对话"},
    "zh-Hant": {"conversations": "{n} 次對話", "monthlyRecovery": "每月 {n} 次挽回對話。", "lifetimeRecovery": "{n} 次終身對話", "pack": "£{n} 方案", "perMonth": "/月", "recoveryEveryMonth": "每月挽回對話"},
}


def load_locale(locale: str) -> dict[str, str]:
    path = ROOT / f"{locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def render_bundle(payload: dict) -> str:
    output = "// Generated by i18n/build-translations.py. Edit locale JSON files, then rebuild.\n"
    output += "window.MODA_TRANSLATIONS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate locale catalogues and build the browser translation bundle.")
    parser.add_argument("--check", action="store_true", help="validate catalogues and fail if translations.js is stale")
    args = parser.parse_args()
    messages = {locale: load_locale(locale) for locale in LOCALES}
    english_keys = list(messages["en"].keys())
    english_set = set(english_keys)

    errors: list[str] = []
    for locale in LOCALES:
        keys = set(messages[locale].keys())
        missing = english_set - keys
        extra = keys - english_set
        if missing:
            errors.append(f"{locale}: missing {len(missing)} keys")
        if extra:
            errors.append(f"{locale}: extra {len(extra)} keys")
        if len(messages[locale]) != len(english_keys):
            errors.append(f"{locale}: expected {len(english_keys)} entries, found {len(messages[locale])}")
    for name, mapping in (("languages", LANGUAGES), ("interface", INTERFACE), ("patterns", PATTERNS)):
        missing_locales = set(LOCALES) - set(mapping)
        if missing_locales:
            errors.append(f"{name}: missing locales {sorted(missing_locales)}")

    if errors:
        raise SystemExit("Translation validation failed:\n- " + "\n- ".join(errors))

    payload = {
        "languages": {locale: LANGUAGES[locale] for locale in LOCALES},
        "interface": {locale: INTERFACE[locale] for locale in LOCALES},
        "patterns": {locale: PATTERNS[locale] for locale in LOCALES},
        "messages": {locale: messages[locale] for locale in LOCALES},
    }
    output = render_bundle(payload)
    output_path = ROOT / "translations.js"
    if args.check:
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != output:
            raise SystemExit("translations.js is stale. Run: python3 i18n/build-translations.py")
        print(f"Translation bundle is up to date: {len(LOCALES)} locales × {len(english_keys)} source strings")
        return

    output_path.write_text(output, encoding="utf-8")
    print(f"Built translations.js: {len(LOCALES)} locales × {len(english_keys)} source strings")


if __name__ == "__main__":
    main()
