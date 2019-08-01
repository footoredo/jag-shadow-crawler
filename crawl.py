import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone, time
from multiprocessing import Pool
import sys

BASE_URL = "https://{}.contest.atcoder.jp".format(sys.argv[1])

def parse_time(time_str):
    return datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S %z")

def get_result(path):
    url = BASE_URL + path
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.table.find_all("tr")

    ret = {}
    ret["problem"] = rows[0].td.text.strip()[0]
    ret["user"] = rows[1].td.text.strip()
    create_time = parse_time(rows[2].td.text.strip()).astimezone(tz=timezone(timedelta(hours=8)))
    start_time = create_time.replace(hour=int(sys.argv[2]), minute=0, second=0)
    ret["time"] = (create_time - start_time).seconds
    ret["is_accepted"] = rows[4].td.span['data-title'] == "Accepted"

    return ret

submission_url = BASE_URL + "/submissions/all/{}"

jobs = []
for i in range(int(sys.argv[3]), int(sys.argv[4])+1):
    url = submission_url.format(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.table
    for row in table.tbody.find_all("tr"):
        jobs.append(row.find_all('a')[-1]["href"])

with Pool(4) as p:
    _results = list(p.map(get_result, jobs))
    results = list(filter(lambda result: result["time"] <= 5*60*60, _results))
    print(json.dumps(results))
