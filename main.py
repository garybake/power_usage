import sys
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import requests

load_dotenv()

def get_db():
    db_location = os.getenv('DB_FILE')
    conn = sqlite3.connect(db_location)
    return conn

def initialise_db():
    conn = get_db()

    print('Opened database successfully')
    conn.execute('DROP TABLE IF EXISTS CONSUMPTION')

    conn.execute('''CREATE TABLE CONSUMPTION (
            PRODUCT             CHAR(50)  NOT NULL,
            INTERVAL_START      REAL,
            INTERVAL_END        REAL,
            CONSUMPTION         REAL,
            PRIMARY KEY (PRODUCT, INTERVAL_START));
    ''')

    print('Table created successfully')
    conn.commit()
    conn.close()
    return

def get_electricity_usage(url=None):
    basic_auth = HTTPBasicAuth(os.getenv('API_KEY'), '')
    
    if not url:
        e_mpan = os.getenv('ELECTRICITY_MPAN')
        e_serial = os.getenv('ELECTRICITY_SERIAL')
        base_url = os.getenv('BASE_URL')
        url = f'{base_url}electricity-meter-points/{e_mpan}/meters/{e_serial}/consumption/'
    
    try:
        resp = requests.get(url, auth=basic_auth)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'Failed response from {url}')
        print(e.request)
        print(e.response)
        sys.exit(1)

    data = resp.json()

    return data

def dt_to_unixtime(dt):
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ').timestamp()

def row_db_format(row):
    start = dt_to_unixtime(row['interval_start'])
    end = dt_to_unixtime(row['interval_end'])
    consumption = row['consumption']
    return [start, end, consumption]

def store(data):
    rows = data['results']
    all_rows = [row_db_format(r) for r in rows]
    conn = get_db()
    c = conn.executemany('REPLACE INTO CONSUMPTION (PRODUCT, INTERVAL_START, INTERVAL_END, CONSUMPTION) VALUES("Electricity", ?,?,?);', all_rows);

    print(f'Inserted {c.rowcount} records.')
		
    conn.commit()
    conn.close()

def main():
    request_count = 1
    data = get_electricity_usage()
    store(data)

    # next_url = data['next']
    # while next_url is not None:
    #     request_count += 1
    #     data = get_electricity_usage(next_url)
    #     store(data)
    #     next_url = data['next']
    #     print(f'requests: {request_count}')

if __name__ == '__main__':
    if not os.path.exists(os.getenv('DB_FILE')):
        print('DB not found... initialising')
        initialise_db()
    main()
