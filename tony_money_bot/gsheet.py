from collections import defaultdict
from datetime import date

import gspread
from cachetools import TTLCache, cached

from tony_money_bot.config import settings


@cached(cache={})
def get_google_table():
    gc = gspread.service_account(filename=settings.GOOGLE_SERVICE_ACCOUNT_FILE)
    return gc.open_by_url(settings.GOOGLE_SHEET_URL)


@cached(cache=TTLCache(maxsize=10, ttl=60 * 10))
def get_full_categories() -> [(str, int)]:
    g_table = get_google_table()
    g_sheet = g_table.worksheet("План")
    results = []
    for row in g_sheet.batch_get(["B4:C17"])[0]:
        if not row:
            continue
        results.append((row[1], int(row[0])))
    return results


def get_categories() -> [str]:
    full_cats = get_full_categories()
    return [name for name, _ in full_cats]


def next_available_row(worksheet, col=2):
    str_list = list(filter(None, worksheet.col_values(col)))
    return str(len(str_list) + 1)


def write_new_spent(amount: float, category: str, name: str):
    g_table = get_google_table()
    g_sheet = g_table.worksheet("Учет")
    row_number = next_available_row(g_sheet)

    g_sheet.update_cell(row_number, 2, str(date.today()))
    g_sheet.update_cell(row_number, 3, amount)
    g_sheet.update_cell(row_number, 4, category)
    g_sheet.update_cell(row_number, 5, name)


def make_report():
    g_table = get_google_table()
    g_sheet = g_table.worksheet("Учет")
    row_number = next_available_row(g_sheet)
    spent_feed = g_sheet.batch_get([f"B2:D{int(row_number) - 1}"], major_dimension="ROWS")[0]
    totals = defaultdict(lambda: 0.0)
    for _, amount, category in spent_feed:
        totals[category] += float(amount.replace(",", "."))

    full_cats = get_full_categories()
    quotas = {}
    for name, amount in full_cats:
        quotas[name] = amount - totals[name]

    return quotas
