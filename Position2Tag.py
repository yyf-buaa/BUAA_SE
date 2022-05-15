
import csv
import sqlite3
conn = sqlite3.connect(database='db.sqlite3')
f = open('adcode.csv', encoding="utf-8")
file = csv.DictReader(f)
for row in file:
    adcode = row['adcode']
    name = row['name']
    if name.endswith('市') and adcode[4:] == '00':
        sql = "insert into app_tag(content, forbidden, forbidden_reason) Values ('%s','0','')"
        rows = conn.execute(sql % (name))
        conn.commit()

conn.close()
