import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from multiprocessing import Pool

def parse_time(time_str):
    return datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S %z")

def get_result(path):
    start_time = parse_time("2012/11/04 10:00:00 +0800")
    url = "https://jag2012autumn.contest.atcoder.jp" + path
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.table.find_all("tr")

    ret = {}
    ret["problem"] = rows[0].td.text.strip()[0]
    ret["user"] = rows[1].td.text.strip()
    create_time = parse_time(rows[2].td.text.strip())
    ret["time"] = (create_time - start_time).seconds
    ret["is_accepted"] = rows[4].td.span['data-title'] == "Accepted"

    return ret

base_url = "https://jag2012autumn.contest.atcoder.jp/submissions/all/{}"

jobs = []
#for i in range(55, 82):
for i in range(55, 82):
    url = base_url.format(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.table
    for row in table.tbody.find_all("tr"):
        jobs.append(row.find_all('a')[-1]["href"])

with Pool(4) as p:
    _results = list(p.map(get_result, jobs))
    results = list(filter(lambda result: result["time"] <= 5*60*60, _results))
    print(json.dumps(results))
