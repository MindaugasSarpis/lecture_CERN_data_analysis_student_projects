
import duckdb 
import os

DB = "vilnius.db"

def export_all(listings_csv = "listings_all.csv", tasks_csv = "logs_all.csv", folder = "result_data"):

    #jei nera folderio padarom
    os.makedirs(folder, exist_ok=True)

    with duckdb.connect(DB) as con:
        #listings
        listings_df = con.sql("SELECT * FROM listings").df()
        listings_df.to_csv(f"{folder}/{listings_csv}", index=False, encoding="utf-8")

        # logs
        tasks_df = con.sql("SELECT * FROM tasks").df()
        tasks_df.to_csv(f"{folder}/{tasks_csv}", index=False, encoding="utf-8")

def export_latest(listings_csv = "listings_latest.csv", tasks_csv = "logs_latest.csv", folder = "result_data"):

    #jei nera folderio padarom
    os.makedirs(folder, exist_ok=True)
    
    with duckdb.connect(DB) as con:
        #listings
        listings_df = con.sql("SELECT * FROM listings ls WHERE ls.task_id IN (SELECT ts.task_id FROM tasks ts ORDER BY ts.task_id DESC LIMIT 4) ").df()
        listings_df.to_csv(f"{folder}/{listings_csv}", index=False, encoding="utf-8")

        #logs
        tasks_df = con.sql("SELECT * FROM tasks ORDER BY task_id DESC LIMIT 4").df()
        tasks_df.to_csv(f"{folder}/{tasks_csv}", index=False, encoding="utf-8")

