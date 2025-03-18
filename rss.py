#!/bin/python3
"""rss feed with one item, with ID of file hash"""

from datetime import timezone, datetime
import os

FILE = "polycule.json"
ISO_DATE = "%Y-%m-%dT%H:%M:%S%z"

mod_date = os.path.getmtime(FILE)
mod_datetime = datetime.fromtimestamp(mod_date, tz=timezone.utc)

with open(FILE, "r", encoding="utf-8") as file:
    contents = file.read()


print("Content-type: application/xml")
print()

print(
    f"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>polycule</title>
    <link href='https://server.alifeee.net/polycule/rss' rel='self' />
    <updated>{mod_datetime.isoformat()}</updated>
    <author>
        <name>alifeee</name>
    </author>
    <id>https://server.alifeee.net/polycule/</id>
    <entry>
        <title>polycule update!</title>
        <link href='https://server.alifeee.net/polycule/' />
        <id>uuid:{hash(contents)}</id>
        <updated>{mod_datetime.isoformat()}</updated>
        <summary>updated!</summary>
    </entry>
</feed>
"""
)
