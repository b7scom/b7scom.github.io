import camelot
import pandas as pd

# Уточненные RGB-значения и их допустимая погрешность (Tolerance)
# NOTE: В PDF RGB-значения могут быть представлены в разных форматах,
# а точное определение заливки ячейки требует анализа графических элементов.
# Этот код фокусируется на извлечении ЧИСЕЛ.

PDF_PATH = r"C:\Users\Admin\Downloads\Год 1 S (2025 КС).pdf"
PAGES = '11-22'
COLOR_RANGES = {
    'orange': (245, 155, 1),  # R G B
    'green': (81, 165, 160),
    'red': (255, 0, 0)  # Указанное вами 81,165,160 для красного ошибочно,
    # я использую более вероятное значение.
}
TOLERANCE = 10  # Погрешность для цветового диапазона (если бы мы его извлекали)


def parse_calendar_tables(pdf_path, pages):
    """
    Извлекает таблицы календаря из указанных страниц PDF с помощью Camelot.

    Примечание: Camelot извлекает только данные; для цвета требуется
    использовать другие библиотеки, такие как pdfplumber, для анализа
    низкоуровневых PDF-объектов.
    """

    # Режим 'lattice' хорошо подходит для таблиц с видимыми линиями,
    # 'stream' для таблиц без них. На вашем примере 'lattice' должен подойти.
    tables = camelot.read_pdf(
        pdf_path,
        pages=pages,
        flavor='lattice',
        # Если таблицы имеют одинаковое расположение, но не заполняют всю страницу,
        # можно использовать table_areas=['x1,y1,x2,y2'] 
    )

    all_parsed_data = []

    print(f"Найдено таблиц: {len(tables)} на страницах {pages}")

    for table in tables:
        df = table.df
        page_number = table.page
        parsed_page_data = []

        # Предполагаем, что таблица имеет структуру 7 столбцов (ПН-ВС)
        # и несколько строк для дней.
        # Каждая ячейка состоит из двух строк: число и персональное число (например, "1\n5 ЛИЧНЫЙ ДЕНЬ")

        # Пропускаем строку заголовков дней недели (ПН, ВТ,...)
        data_rows = df.iloc[1:]

        for _, row in data_rows.iterrows():
            for i, cell_content in enumerate(row):
                if cell_content and isinstance(cell_content, str):
                    # Разбиваем содержимое ячейки на число и персональное число
                    parts = cell_content.strip().split('\n', 1)
                    if len(parts) == 2:
                        day_number = parts[0].strip()
                        personal_number_text = parts[1].strip()

                        # Извлечение только персонального числа (если нужно)
                        try:
                            # Ожидаем: "5 ЛИЧНЫЙ ДЕНЬ" -> 5
                            personal_number = int(personal_number_text.split(' ')[0])
                        except ValueError:
                            personal_number = None

                        # Сохраняем извлеченные данные
                        parsed_page_data.append({
                            'page': page_number,
                            'day_number': day_number,
                            'personal_number': personal_number,
                            # Здесь должно быть место для определения цвета,
                            # но это требует другой библиотеки (например, pdfplumber)
                            'color': 'unknown'
                        })

        all_parsed_data.extend(parsed_page_data)

    return pd.DataFrame(all_parsed_data)


# --- Часть для извлечения цвета с pdfplumber (сложная, как концепция) ---

# *Если* вы решите использовать pdfplumber, то идея такая:
# 1. Открыть PDF с pdfplumber.
# 2. Итерироваться по страницам 11-22.
# 3. Получить графические объекты (`page.rects`, `page.curves`, `page.non_stroking_color`)
#    для определения заливки ячейки.
# 4. Получить текстовые объекты (`page.chars`) с их координатами.
# 5. Сопоставить координаты текстовых объектов (чисел) с координатами заливки ячейки.

# --- Запуск функции ---

# Укажите путь к вашему PDF-файлу
# extracted_data = parse_calendar_tables(PDF_PATH, PAGES)
# print(extracted_data.head())
# extracted_data.to_csv('extracted_calendar_data.csv', index=False)

print("Для извлечения числовых данных используйте Camelot (пример кода выше).")
print(
    "Для извлечения цвета заливки ячейки необходимо использовать более низкоуровневые библиотеки (например, pdfplumber) для анализа графических объектов PDF и сопоставления их с координатами извлеченных чисел, что является более сложной задачей.")
print("Учитывая, что в извлеченных данных цвет будет 'unknown', я предоставляю структуру для получения чисел.")
