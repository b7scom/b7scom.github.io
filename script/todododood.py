# -*- coding: utf-8 -*-
"""
Автоматический парсер PDF годов и генератор JSON.
Форматирует файл в структуру:
{
  "year": 2025,
  "personal_year": {...},
  "personal_day_descriptions": {...},
  "day_by_color": {...},
  "to_do": {...},
  "not_to_do": {...},
  "calendar": {...}
}

Зависимости:
    pip install pdfplumber
"""

import re
import json
import pdfplumber
from pathlib import Path

# ========== Настройки ==========
INPUT_PDF = r"C:\Users\Admin\Downloads\Год {} S (2025 СК1ё).pdf"
OUTPUT_DIR = Path(".")

# Если нужно автоматически нумеровать JSON-файлы
def get_json_name(pdf_name: str) -> str:
    match = re.search(r"Год\s*(\d+)", pdf_name)
    num = match.group(1) if match else "X"
    return f"Ncalendar_{num}.json"


# ========== Функции ==========
def extract_page_text(pdf, page_num):
    """Извлечь текст одной страницы"""
    try:
        return pdf.pages[page_num - 1].extract_text() or ""
    except IndexError:
        return ""


def parse_pdf_to_json(pdf_path):
    """Основная функция: извлекает данные по страницам и собирает JSON"""
    result = {
        "year": 2025,
        "personal_year": {},
        "personal_day_descriptions": {},
        "day_by_color": {},
        "to_do": {},
        "not_to_do": {},
        "calendar": {}
    }

    with pdfplumber.open(pdf_path) as pdf:
        # ---------- Страница 10: personal_year ----------
        page10 = extract_page_text(pdf, 10)
        if page10:
            title_match = re.search(r"Год\s+[^\n]+", page10)
            result["personal_year"]["title"] = title_match.group(0).strip() if title_match else "Не найдено"
            result["personal_year"]["year_description"] = re.sub(r"^Год\s+[^\n]+\n?", "", page10).strip()

        # ---------- Страницы 6-7: personal_day_descriptions ----------
        day_text = extract_page_text(pdf, 6) + "\n" + extract_page_text(pdf, 7)
        day_blocks = re.split(r"\n\s*(?=\d\s|1\s)", day_text)
        for block in day_blocks:
            match = re.match(r"(\d)\s*(.+)", block.strip(), re.S)
            if match:
                num, desc = match.groups()
                result["personal_day_descriptions"][num] = desc.strip()

        # ---------- Страница 8: day_by_color ----------
        page8 = extract_page_text(pdf, 8)
        colors = {
            "red": r"Красн\w*[:\-–]\s*(.+)",
            "orange": r"Оранж\w*[:\-–]\s*(.+)",
            "green": r"Зел[её]н\w*[:\-–]\s*(.+)"
        }
        for key, pattern in colors.items():
            match = re.search(pattern, page8, re.I)
            if match:
                result["day_by_color"][key] = match.group(1).strip()

        # ---------- Страница 9: to_do / not_to_do ----------
        page9 = extract_page_text(pdf, 9)
        # to_do
        todo_matches = re.findall(r"(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота|Воскресенье)\s*[:\-–]\s*([^\n]+)", page9)
        week_map = {
            "Понедельник": "mon",
            "Вторник": "tue",
            "Среда": "wed",
            "Четверг": "thu",
            "Пятница": "fri",
            "Суббота": "sat",
            "Воскресенье": "sun"
        }
        for day, text in todo_matches:
            key = week_map.get(day, day)
            result["to_do"][key] = text.strip()

        # not_to_do
        nottodo_matches = re.findall(r"Не\s+[^\n]+", page9)
        if nottodo_matches:
            for i, day in enumerate(result["to_do"].keys()):
                result["not_to_do"][day] = nottodo_matches[i] if i < len(nottodo_matches) else ""

        # ---------- Страницы 11–22: calendar ----------
        for i, month in enumerate([
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ], start=11):
            text = extract_page_text(pdf, i)
            if not text.strip():
                continue
            # ищем абзац, начинающийся с "Месяц"
            match = re.search(r"(Месяц[^\n]+(?:\n.+)+)", text)
            if match:
                desc = match.group(1).strip()
                result["calendar"][month] = {"personal_month_description": desc}
            else:
                result["calendar"][month] = {"personal_month_description": text.strip()[:500]}

    return result


# ========== Запуск ==========
def main():
    for i in range(6, 10):
        pdf_path = Path(INPUT_PDF.format(i))
        if not pdf_path.exists():
            print(f"❌ Файл {pdf_path} не найден.")
            return

        result = parse_pdf_to_json(pdf_path)
        out_name = get_json_name(pdf_path.name)
        out_path = OUTPUT_DIR / out_name

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON сохранён как {out_name}")


if __name__ == "__main__":
    main()
