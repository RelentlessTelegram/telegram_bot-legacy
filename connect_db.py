
import psycopg2
import asyncio
import json
from urllib.parse import urlparse

async def get_from_table(conn, table_name, chatid, database_url):
    while True:
        try:
            # create a cursor
            cur = conn.cursor()
            cur.execute("select * from {} where chatid = '{}'".format(table_name, chatid))
            records = cur.fetchall()
            cur.close()
            return records
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue
        
        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def get_all_from_table(conn, table_name, database_url):
    while True:
        try:
            # create a cursor
            cur = conn.cursor()
            cur.execute("SELECT * FROM {}".format(table_name))
            records = cur.fetchall()
            cur.close()
            return records
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def add_into_table(conn, table_name, dict, database_url):
    while True:
        try:
            # read connection parameters
            # connect to the PostgreSQL server
            # create a cursor
            cur = conn.cursor()
            columns = []
            values = []
            for x in dict:
                columns.append(x)
                values.append("'" + dict[x] + "'")
            columns = ",".join(columns)
            values = ",".join(values)
            cur.execute('''INSERT INTO {}({})
            VALUES ({})
            '''.format(table_name, columns, values)
            )
            conn.commit()
            cur.close()
            return "Done"

        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break



async def update_in_table(conn, table_name, condition, parameter, dict, database_url):
    while True:
        try:
            cur = conn.cursor()
            set_data = ""
            for x in dict:
                set_data += x + "= '" + dict[x] + "',"
            set_data = set_data[0:-1]
            string = '''UPDATE {}
            SET {}
            WHERE {} = '{}'
            '''
            cur.execute(string.format(table_name, set_data, condition, parameter))
            conn.commit()
            cur.close()
            return "Done"
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break
    
async def update_all_in_table(conn, table_name, condition, parameter, database_url):
    while True:
        try:
            cur = conn.cursor()
            string = '''UPDATE {}
            SET {} = '{}'
            '''
            cur.execute(string.format(table_name, condition, parameter))
            conn.commit()
            cur.close()
            return "Done"
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue
        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break




async def delete_from_table(conn, table_name, condition, parameter, database_url):
    while True:
        try:
            cur = conn.cursor()
            string = '''DELETE FROM {}
            WHERE {} = '{}'
            '''
            cur.execute(string.format(table_name, condition, parameter))
            conn.commit()
            cur.close()
            return "Done"
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def get_one_column_from_table(conn, table_name, condition, database_url):
    while True:
        try:
            cur = conn.cursor()
            string = '''SELECT DISTINCT {} FROM {};
            '''
            cur.execute(string.format(condition, table_name))
            records = cur.fetchall()
            conn.commit()
            cur.close()
            return records
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def init_database(conn, database_url):
    while True:
        try:
            # create a cursor
            cur = conn.cursor()
            cur.execute('''SELECT EXISTS (
    SELECT FROM 
        pg_tables
    WHERE 
        schemaname = 'public' AND 
        tablename  = 'admin'
    );''')  
            result = cur.fetchone()
            if result[0] == True:
                return "Initalized"

            cur.execute('''CREATE TABLE IF NOT EXISTS public.admin
(
    chatid character varying(50) NOT NULL,
    PRIMARY KEY (chatid)
);

ALTER TABLE IF EXISTS public.admin
    OWNER to postgres;''')

            conn.commit()
            cur.execute('''CREATE TABLE IF NOT EXISTS public.chat_details
(
    chatid character varying(50)  NOT NULL,
    userid character varying(255),
    name character varying(50),
    birthday character varying(50),
    housing character varying(255),
    CONSTRAINT chat_details_pkey PRIMARY KEY (chatid)
);

ALTER TABLE IF EXISTS public.chat_details
    OWNER to postgres;
            ''')
            conn.commit()
            cur.execute('''CREATE TABLE IF NOT EXISTS public.sf_reminder
(
    chatid character varying(50) NOT NULL,
    done character varying(50),
    CONSTRAINT sf_reminder_pkey PRIMARY KEY (chatid)
);

ALTER TABLE IF EXISTS public.sf_reminder
    OWNER to postgres;''')
            conn.commit()
            cur.execute('''CREATE TABLE IF NOT EXISTS public.wishes_reminder
(
    chatid character varying(50)NOT NULL,
    name character varying(50),
    wishes_not_done character varying(255),
    CONSTRAINT wishes_reminder_pkey PRIMARY KEY (chatid)
);

ALTER TABLE IF EXISTS public.wishes_reminder
    OWNER to postgres;''')
            cur.close()
            return "Done"
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def check_id_in_table(conn, table_name, parameter, database_url):
    while True:
        try:
            print(type(parameter))
            cur = conn.cursor()
            string = '''select exists(select 1 from {} where chatid='{}');''' 
            cur.execute(string.format(table_name, parameter))
            result = cur.fetchone()
            return result[0]

        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def all_tables(conn, database_url):
    while True:
        try:
            cur = conn.cursor()
            string = '''SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
            '''
            cur.execute(string)
            records = cur.fetchall()
            conn.commit()
            cur.close()
            return records
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break

async def get_column_titles_from_table(conn, table_name ,database_url):
    while True:
        try:
            cur = conn.cursor()
            string = '''select column_name
from information_schema.columns
where table_name = '{}'
            '''
            cur.execute(string.format(table_name))
            records = cur.fetchall()
            conn.commit()
            cur.close()
            return records
        
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            database = urlparse(database_url)
            conn = psycopg2.connect(
            host=database.hostname,
            user=database.username,
            password=database.password,
            port=database.port,
            keepalives= 1,
            keepalives_idle = 5,
            keepalives_interval=2,
            keepalives_count = 2)
            continue

        except psycopg2.DatabaseError as error:
            print(error)
            conn.commit()
            break
def main():
    pass

if __name__ == "__main__":
    main()

