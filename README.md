Small script to download energy usage data using the octopus energy api.

API docs  
https://developer.octopus.energy/docs/api/

Dashboard  
https://octopus.energy/dashboard/developer/ 

Use the dashboard to obtain api keys.

Create a .env file and populate as in the example below with your own values

    DB_FILE=logs.db
    BASE_URL=https://api.octopus.energy/v1/

    API_KEY=***
    ELECTRICITY_MPAN=***
    ELECTRICITY_SERIAL=***

Outputs a sqlite db with a CONSUMPTION table showing half hourly usage.

To read into a dataframe (for science!)

    con = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * from CONSUMPTION", con)
    con.close()
