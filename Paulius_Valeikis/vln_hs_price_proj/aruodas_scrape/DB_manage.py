# db_manager.py
import duckdb
from pathlib import Path
from datetime import date, datetime, timezone
import pandas as pd
from .html_parse import SCHEMA


class DBManager:
    def __init__(self, db_path: str = "vilnius.db"):
        self.db_path = Path(db_path)
        self.con = duckdb.connect(str(self.db_path))
        self.run_date = date.today()
        self.task_id = None

    #iniciajuoja lenteteles jei leidziama pirma karta
    def ensure_schema(self):
       self.create_tasks_table()
       self.create_table_from_schema()

    #dinamiskai sugeneruoja lenteliu sql
    def create_sql_from_schema(self):
        with open("aruodas_scrape/SQL/create_listing_stg_table.sql", "w") as f:
            sql = """CREATE TABLE IF NOT EXISTS listings_stg (
            """
            sql = sql + f"\n{SCHEMA[0]} TEXT"
            for field in SCHEMA[1:]:
                sql = sql + ",\n"
                sql = sql + f"{field} TEXT"
                

            sql = sql + ");"
            f.write(sql)

        with open("aruodas_scrape/SQL/create_listing_table.sql", "w") as f:
            sql = """CREATE TABLE IF NOT EXISTS listings (
            """
            sql = sql + f"\n{SCHEMA[0]} TEXT"
            for field in SCHEMA[1:]:
                sql = sql + ",\n"
                sql = sql + f"{field} TEXT"
                

            sql = sql + ");"  

            f.write(sql) 


    def create_table_from_schema(self):
        self.create_sql_from_schema()
        with open("aruodas_scrape/SQL/create_listing_stg_table.sql", "r") as f:
            sql = f.read()
            self.con.execute(sql)
        with open("aruodas_scrape/SQL/create_listing_table.sql", "r") as f:
            sql = f.read()
            self.con.execute(sql)
        

    def create_tasks_table(self):
        with open("aruodas_scrape/SQL/create_task_seq.sql", "r") as f:
            sql = f.read()
            self.con.execute(sql)
        with open("aruodas_scrape/SQL/create_task_table.sql", "r") as f:
            sql = f.read()
            self.con.execute(sql)
        
    #funkcija loginimui
    def start_task(self, category=None, pages=None):
        start_time = datetime.now(timezone.utc)

        self.con.execute("""
            INSERT INTO tasks (run_date, category, start_time, status, pages)
            VALUES (?, ?, ?, 'running', ?);
        """, [self.run_date, category, start_time, pages])

        # paimam paskutinį įrašytą task_id
        self.task_id = self.con.execute("""
            SELECT task_id
            FROM tasks
            ORDER BY task_id DESC
            LIMIT 1;
        """).fetchone()[0]
    #funkcija loginimui pabaigt
    def finish_task(self, records=0, error=None):
       
        end_time = datetime.now(timezone.utc)
        status = "failed" if error else "success"

        self.con.execute("""
            UPDATE tasks
            SET end_time = ?, status = ?, records = ?, error = ?
            WHERE task_id = ?;
        """, [end_time, status, records, error, self.task_id])
    # apvalom nuo seno run
    #tuo paciu metu galima zvilgtelt i stg lentelel jei paskutinis runas buvo blogas
    def begin_run(self):
        self.con.execute("""TRUNCATE TABLE listings_stg;
        """)
    #funkcija imetimui eiluciu pagal zodyna
    def insert_row(self, row_dict: dict, category):

        
        url = row_dict.get("url")
        row_dict["listing_id"] = extract_listing_id(url)
        row_dict["task_id"] = self.task_id
        row_dict["ext_date"] = date.today()
        row_dict["category"] = category

      
        df = pd.DataFrame([row_dict])
        self.con.register("tmp", df)
    
        self.con.execute("INSERT INTO listings_stg SELECT * FROM tmp;")
        self.con.unregister("tmp")

    #jei parejo be klaidu imetam viska i galutine laikymo lentele
    def finalize(self):
        self.con.execute("INSERT INTO listings SELECT * FROM listings_stg;")

    #Close the connection
    def close(self):
        if self.con:
            self.con.close()


#helper funkcija unikaliu id generavimui
def extract_listing_id(url: str) -> str:
    #Return id like '2-1679105_2025-11-13'
    if not url:
        return None
    listing_code = url.split("/")[1]

    #timeseries data unique id
    today = date.today().isoformat()
    return f"{listing_code}_{today}"

