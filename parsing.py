import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3

# BS = BeautifulSoup()

COUNT_ADDED = 0
COUNT_IN_BASE = 0

DB_FILENAME: str = "database.db"
DB_EXISTS = os.path.exists(DB_FILENAME)

con = sqlite3.connect("database.db")
cur = con.cursor()

# Check exists database.
if not DB_EXISTS:
    print("Creating database...")
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS judges USING fts4(
            --id INTEGER PRIMARY KEY,
            name TEXT,
            total_decisions TEXT,
            granted_asylum TEXT,
            granted_other_relief TEXT,
            denied TEXT
        )
    """)
    con.commit()

    print("Done.")
else:
    print("Database exists.")


def search_name(name):
    cur.execute("""
        SELECT *, MATCHINFO(judges) FROM judges WHERE name MATCH ?
    """, (name,))
    res = []
    tbl: list = ["Name Judge", "Total Decisions", "% Granted Asylum",
                 "% Granted Other Relief", "% Denied"]
    tmp = cur.fetchall()
    lst = []
    for row in tmp:
        lst.append(row[:-1])
    for row in range(len(lst)):
        count = 0
        res.append([])
        while count < 5:
            s: str = tbl[count] + ": " + (lst[row][count])
            res[row].append(s)
            count += 1
    return res


def check_exists_judge(name: str) -> bool:
    """check the judge in the database"""
    tmp = cur.execute("SELECT name FROM judges WHERE name MATCH ?", (name,))
    res = tmp.fetchone()
    try:
        if len(res) >= 1:
            return False
        else:
            return True
    except TypeError as er:
        print(er, name)
        return True


def add_judge() -> list:
    """adding parsed data to a list"""
    data_judge: list = []
    result: list[list] = []
    index: int = 0

    with open("base_judge.html") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    all = soup.find(class_="text-xs md:text-sm font-mono").find_all("td")

    for el in all:
        data_judge.append(el.text.strip())

    for elem in data_judge:
        if elem == "":
            idx = data_judge.index(elem)
            res = data_judge[idx]
            res2 = data_judge[idx + 1]
            data_judge.remove(res)
            data_judge.remove(res2)

    for i in range(int(len(data_judge) / 5)):
        result.append([])
        for x in range(5):
            result[i].append(data_judge[index])
            index += 1
    return result


def insert_base(name: tuple) -> None:
    """adding judge data to the table"""
    global COUNT_ADDED, COUNT_IN_BASE
    if check_exists_judge(name[0]):
        cur.execute("""INSERT INTO judges (name, total_decisions, granted_asylum, granted_other_relief, denied)
                    VALUES (?, ?, ?, ?, ?)""", name)
        con.commit()
        COUNT_ADDED += 1
    else:
        COUNT_IN_BASE += 1
    print(COUNT_IN_BASE)
    return


# URL: str = "https://trac.syr.edu/immigration/reports/judgereports/"

# HEADERS: dict = {
#     "Accept": "*/*",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.771 YaBrowser/23.11.2.771 Yowser/2.5 Safari/537.36"
# }

# DATE_UPDATE = datetime(2024, 1, 1)
# DATE_NOW = datetime.now()
# PERIOD_UPD = int(30)

# DAY = DATE_NOW - DATE_UPDATE


# if DAY.days > PERIOD_UPD and DAY.days > 0:
#     req = requests.get(url=URL, headers=HEADERS)
#     src = req.text

#     DATE_UPDATE = PERIOD_UPD

#     with open("base_judge.html", "w") as file:
#         file.write(src)

    # for i in add_judge():
    # row = tuple(i)
    # insert_base(row)

# elif DAY.days < PERIOD_UPD and DAY.days >= 0:
#     print("less")

# else:
#     print("anythink error")


def base():
    DATE_UPDATE = datetime(2024, 3, 1)
    DATE_NOW = datetime.now()
    PERIOD_UPD = int(30)

    DAY = DATE_NOW - DATE_UPDATE

    print(f"последняя проверка - {DAY.days} день/дней назад.")
    # if DAY.days > PERIOD_UPD and DAY.days > 0:
    #     print("Base updating")
    #     req = requests.get(url=URL, headers=HEADERS)
    #     src = req.text

    #     DATE_UPDATE = PERIOD_UPD

    #     with open("base_judge.html", "w") as file:
    #         file.write(src)

