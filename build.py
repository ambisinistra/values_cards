"""
Собирает страницу из единых источников:
  value_cards.py        — 100 карточек (EN / RU / HU) и привязка к Шварцу
  prompts/analysis_*.md — промпт анализа на трёх языках, токен {{LAYOUT}}
  src/template.html     — разметка, стили и логика страницы

Выход:
  index.html             — полный документ для GitHub Pages и для пересылки файлом
  dist/artifact.html     — тело страницы без <html>/<head> (для публикации как Artifact)

Запуск: python build.py
"""

import json
import re
from pathlib import Path

from value_cards import CARDS, LANGS, validate

ROOT = Path(__file__).parent
TOKEN = "{{LAYOUT}}"


def load_prompts() -> dict:
    prompts = {lang: (ROOT / "prompts" / f"analysis_{lang}.md").read_text(encoding="utf-8") for lang in LANGS}
    shape = {}
    for lang, text in prompts.items():
        assert text.count(TOKEN) == 1, f"{lang}: {TOKEN} must appear exactly once"
        assert text.rstrip().endswith(TOKEN), f"{lang}: data must come last"
        shape[lang] = (len(re.findall(r"^## ", text, re.M)), len(re.findall(r"^\d+\. \*\*", text, re.M)),
                       len(re.findall(r"^- \*\*", text, re.M)))
    assert len(set(shape.values())) == 1, f"prompt structure differs between languages: {shape}"
    return prompts


def page_cards() -> list:
    return [{
        "id": c["id"], "key": c["key"], "ho": c["higher_order"], "conf": c["confidence"],
        **{lang: [c[f"name_{lang}"], c[f"def_{lang}"]] for lang in LANGS},
    } for c in CARDS]


def main() -> None:
    validate()
    template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    js = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for marker, value in (("/*__CARDS__*/[]", js(page_cards())), ("/*__PROMPTS__*/{}", js(load_prompts()))):
        assert template.count(marker) == 1, marker
        template = template.replace(marker, value)

    head, body = template.split("<!--BODY-->")
    head = head.replace("<!--HEAD-->", "").strip()
    body = body.strip()

    full = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n")
    (ROOT / "index.html").write_text(full, encoding="utf-8")
    (ROOT / "dist").mkdir(exist_ok=True)
    (ROOT / "dist" / "artifact.html").write_text(f"{head}\n{body}\n", encoding="utf-8")
    print(f"index.html {len(full.encode()) / 1024:.0f} KB, dist/artifact.html written")


if __name__ == "__main__":
    main()
