import psycopg2
import simp_config

con = psycopg2.connect(database=simp_config.psql_samsara["database"], user=simp_config.psql_samsara["user"], password=simp_config.psql_samsara["password"])
cursor = con.cursor()

def get_last_cell_situation_row():
    """

    GETS LAST CELL SITUATION ENTRY

    """
    cursor.execute("select * from cell_situation order by id desc limit 1;")
    return cursor.fetchone()

def get_event_row(table_name, row_id):
    """

    GETS EVENTS ENTRY

    """
    cursor.execute("select * from " + str(table_name) + " where id = " + str(row_id) + ";")
    return cursor.fetchone()

def get_last_row(table_name):
    """

    GETS LAST ROW ENTRY

    """
    cursor.execute("select * from " + str(table_name) + " WHERE id=(SELECT max(id) FROM "+ str(table_name) +";")
    return cursor.fetchone()
