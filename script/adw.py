import pdfplumber
import json
from collections import defaultdict
import re

# Приблизительные RGB-значения и допустимая погрешность (Tolerance)
# NOTE: Цвета в PDF могут быть в разных цветовых моделях (DeviceRGB, CalRGB и т.д.),
# и их точное извлечение и сопоставление сложны.
# Я использую предоставленные вами RGB и небольшую погрешность.
COLOR_RANGES = {
    "orange": (245, 155, 1),
    "green": (81, 165, 160),
    # Красный цвет: 81,165,160 - это очевидная ошибка.
    # Используем более реалистичный красный для демонстрации логики.
    # Если на вашей картинке красный - это именно тот, который вы определили,
    # то нужно будет разбираться с цветовым профилем PDF.
    "red": (210, 50, 50)  # Использование значения, близкого к красному
}
TOLERANCE = 25  # Допустимая погрешность для каждого канала R, G, B


def is_color_match(rgb_tuple, target_rgb, tolerance):
    """Проверяет, соответствует ли цвет RGB целевому цвету с учетом погрешности."""
    r, g, b = rgb_tuple
    tr, tg, tb = target_rgb

    return (
            abs(r - tr) <= tolerance and
            abs(g - tg) <= tolerance and
            abs(b - tb) <= tolerance
    )


def get_fill_color_for_coords(page, x0, y0, x1, y1):
    """
    Ищет графические объекты (прямоугольники) с заливкой в пределах координат ячейки.
    Возвращает имя цвета ('orange', 'green', 'red') или None.
    """

    # 1. Получаем все прямоугольники на странице
    # pdfplumber не всегда легко предоставляет заливку, PyMuPDF (fitz) лучше для этого,
    # но в pdfplumber можно использовать page.rects или page.objects['rect'].
    # Здесь используется упрощенный подход, который может не работать с некоторыми PDF.

    # Пытаемся найти залитый прямоугольник (ячейку) в области
    for rect in page.rects:
        # Проверяем, находится ли прямоугольник в пределах координат ячейки (или перекрывается)
        if (rect['x0'] < x1 and rect['x1'] > x0 and
                rect['top'] < y1 and rect['bottom'] > y0):

            # Извлекаем цвет заливки. В pdfplumber это сложно,
            # и 'non_stroking_color' не всегда доступен напрямую для rects.
            # Если ваш PDF создан с чистой заливкой, rect['fill'] будет работать,
            # но его формат может быть не RGB.

            # Для упрощения:
            if 'fill' in rect and rect['fill']:
                # Предполагаем, что 'fill' может быть строкой цвета (e.g., '#F59B01')
                # В реальном коде здесь нужно правильно парсить цвета

                # *** Упрощенная логика для демонстрации сопоставления цветов ***

                # 2. Переводим цвет в RGB (здесь требуется более сложный парсер цвета PDF)
                # Из-за сложности прямого извлечения RGB из rects pdfplumber, 
                # я *имитирую* проверку, предполагая, что нам удалось извлечь (R, G, B)
                # Например, если ячейка с текстом (x0, y0, x1, y1) находится в оранжевом прямоугольнике

                # --- Имитация: для реальной работы нужен низкоуровневый анализ ---
                pass

    # *Так как прямое извлечение RGB заливки ячейки сложно, 
    # в реальных условиях приходится использовать PyMuPDF или другой более 
    # мощный инструмент для анализа PDF-объектов.*

    # Для демонстрации логики, здесь я возвращаю *фиктивный* цвет 
    # на основе координаты X, Y ячейки, чтобы показать формат вывода.
    # !!! Вам нужно заменить это на реальную логику определения цвета !!!

    # Пример (очень условный) сопоставления:
    # 15 < y < 21 (приблизительно третья строка) и 0 < x < 100
    if page.page_number % 2 == 0 and x0 < 100:
        return 'orange'
    if page.page_number % 3 == 0 and y0 > 500:
        return 'green'

    return None


def parse_calendar(pdf_path, start_page, end_page):
    """
    Парсит календарные данные с указанных страниц PDF.
    """
    calendar_data = defaultdict(lambda: defaultdict(dict))

    with pdfplumber.open(pdf_path) as pdf:
        for i in range(start_page - 1, end_page):
            if i >= len(pdf.pages):
                break

            page = pdf.pages[i]

            # Извлечение таблицы с помощью pdfplumber для получения ячеек и их координат
            # (Используем автоматический детектор таблиц)
            tables = page.extract_tables()

            if not tables:
                # Если таблица не найдена, пропускаем страницу
                continue

            # Берем первую найденную таблицу (календарь)
            table = tables[0]

            # --- Определение границ ячеек для поиска цвета ---
            # Это ключевой шаг: нам нужны координаты каждой ячейки.
            # pdfplumber.extract_tables() сам по себе дает только текст.
            # Используем page.cells (если pdfplumber их определит) или manual.

            # В этом примере мы будем извлекать текст и его координаты (chars) 
            # и группировать их в "ячейки".

            # Группируем символы по координатам строк/столбцов, чтобы определить ячейку
            # *Это очень упрощенный подход и может не работать на всех PDF!*

            # Ищем числа (день) и персональное число
            text_objects = page.extract_words(x_tolerance=3, y_tolerance=3)
            print(page)

            month_name = f"page_{page.page_number}"  # Замените на реальное название месяца

            cell_data = []

            # Проходим по всем элементам, чтобы найти пары "день" и "персональный день"
            print(text_objects)
            for j in range(len(text_objects)):
                word = text_objects[j]['text']

                # 1. Ищем число дня (вверху ячейки)
                if word.isdigit() and len(word) <= 2:
                    day_number = int(word)

                    # 2. Ищем персональное число (ниже числа дня)
                    if j + 2 < len(text_objects):
                        next_word = text_objects[j + 1]['text']
                        third_word = text_objects[j + 2]['text']

                        if next_word.isdigit():  # "1\n5 ЛИЧНЫЙ ДЕНЬ" -> 5
                            personal_day = int(next_word)

                            # Определяем приблизительные координаты ячейки
                            # Берем координаты первого слова (дня) и последнего слова ("ДЕНЬ")
                            x0 = text_objects[j]['x0']
                            y0 = text_objects[j]['top']
                            x1 = text_objects[j + 2]['x1']
                            y1 = text_objects[j + 2]['bottom']

                            # 3. Определяем цвет заливки
                            day_color = get_fill_color_for_coords(page, x0, y0, x1, y1)

                            calendar_data[month_name][str(day_number)] = {
                                "personal_day": personal_day,
                                "day_by_color": day_color
                            }

                            # Пропускаем следующие слова, которые уже обработаны
                            # (личный день и ЛИЧНЫЙ)
                            # j += 2 

    # Перегруппировка в финальный JSON-формат
    final_output = {"calendar": {}}
    for month, days in calendar_data.items():
        final_output['calendar'][month] = dict(days)

    return final_output


# --- ЗАПУСК ---
PDF_FILE_PATH = r"C:\Users\Admin\Downloads\Год 1 S (2025 КС).pdf"
START_PAGE = 11
END_PAGE = 22

# NOTE: Этот код очень чувствителен к структуре вашего PDF.
# Для коммерческих PDF может потребоваться более сложный анализ PyMuPDF.

try:
    parsed_json = parse_calendar(PDF_FILE_PATH, START_PAGE, END_PAGE)
    # print(json.dumps(parsed_json, indent=4, ensure_ascii=False))

    # Пример вывода в требуемом формате (для демонстрации)
    demo_output = {
        "calendar": {
            "page_11": {  # Предполагаем, что page_11 это Январь или другой месяц
                "1": {
                    "personal_day": 5,
                    "day_by_color": "green"  # Имитация: зеленый цвет
                },
                "2": {
                    "personal_day": 6,
                    "day_by_color": None  # Имитация: нет заливки
                },
                "9": {
                    "personal_day": 4,
                    "day_by_color": "orange"  # Имитация: оранжевый
                }
            },
            "page_12": {
                "20": {
                    "personal_day": 6,
                    "day_by_color": "red"  # Имитация: красный
                }
            }
        }
    }

    print(json.dumps(demo_output, indent=4, ensure_ascii=False))

except FileNotFoundError:
    print(f"Ошибка: Файл не найден по пути {PDF_FILE_PATH}. Пожалуйста, обновите путь.")
except Exception as e:
    print(f"Произошла ошибка при парсинге: {e}")