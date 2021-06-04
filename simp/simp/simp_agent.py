import psycopg2
import simp_config

#con = psycopg2.connect(database=simp_config.timescale_simp["database"], user=simp_config.timescale_simp["user"], password=simp_config.timescale_simp["password"])
con = psycopg2.connect("host='20.197.231.34' dbname='simp' user='postgres' password='superc0dex'")
cursor = con.cursor()

def get_last_entry(table_name):
    """

    GETS LAST ENTRY IN TABLE

    """
    cursor.execute("select * from " + str(table_name) + " order by time desc limit 1;")
    return cursor.fetchone()

def get_last_cell_situation_row():
    """

    GETS LAST ENTRY IN CELL_SITUATION

    """
    #	"time", active_hosts, inactive_hosts, underloaded_hosts, overloaded_hosts
    cursor.execute("select * from cell_situation order by time desc limit 1;")
    return cursor.fetchone()

def insert_into_cell_situation(data):
    """

    INSERTS INTO CELL SITUATION

    """
    #	"time", active_hosts, inactive_hosts, underloaded_hosts, overloaded_hosts
    formatted_data = ', '.join(['NOW()', str(data[1]), str(data[2]), str(data[3]), str(data[4])])
    cursor.execute("insert into cell_situation values(" + formatted_data + ");")
    con.commit()
    print("insert into cell_situation has been successfull.")

def insert_into_migration_events(data):
    """

    INSERTS INTO MIGRATION EVENTS

    """
    #	"time", host_dest, instance, status, elapsed_time, created_at
    formatted_data = ', '.join(['NOW()', format_string_value(data[1]), format_string_value(data[2]), format_string_value(data[3]), str(data[4]), format_string_value(data[5])])
    cursor.execute("insert into migration_events values (" + formatted_data + ");")
    con.commit()
    print("insert into migration_events has been successfull.")

def insert_into_host_resources_usage(data):
    """

    INSERTS INTO HOST RESOURCES USAGE

    """
    #	"time", hostname, compute_utilization, memory_utilization, created_at
    formatted_data = ', '.join(['NOW()', format_string_value(data[1]), str(data[2]), str(data[3]), format_string_value(data[4])])
    cursor.execute("insert into host_resources_usage values (" + formatted_data + ");")
    con.commit()
    print("insert into host_resources_usage has been successfull.")


def insert_into_host_situation(data):
    """

    INSERTS INTO HOST SITUATION

    """
    #	"time", hostname, uuid, used_compute, available_compute, used_memory, available_memory, created_at, instances, instances_number, last_change_at, situation
    formatted_data = ', '.join(['NOW()', format_string_value(data[1]), format_string_value(data[2]),
                                str(data[3]), str(data[4]), str(data[5]), str(data[6]), format_string_value(data[7]),
                                format_string_value(data[8]), str(data[9]), format_string_value(data[10]), format_string_value(data[11])])
    cursor.execute("insert into host_situation values (" + formatted_data + ");")
    con.commit()
    print("insert into host_situation has been successfull.")

def format_string_value(data):
    return str("'" + data + "'")
