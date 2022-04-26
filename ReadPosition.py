
import csv
import sqlite3
conn = sqlite3.connect(database='db.sqlite3')
f = open('adcode.csv', encoding="utf-8")
file = csv.DictReader(f)
for row in file:
    adcode = row['adcode']
    name = row['name']
    longitude = row['longitude']
    latitude = row['latitude']
    sql = "insert into app_position(id, name, longitude, latitude, description, visibility) Values ('%s', '%s', '%s', '%s', '', '1')"
    rows = conn.execute(sql % (adcode, name, longitude, latitude))
    conn.commit()

conn.close()
