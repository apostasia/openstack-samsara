import psycopg2
from psycopg2_pgevents.trigger import install_trigger, install_trigger_function, uninstall_trigger, uninstall_trigger_function
from psycopg2_pgevents.event import poll, register_event_channel, unregister_event_channel
import simp_config
import simp_handler

class event():
    def __init__(self,uuid,row_id,table,schema,type):

        self.uuid = uuid
        self.row_id = row_id
        self.table = table
        self.schema = schema
        self.type = type

class listener():
    def __init__(self, host, user, password, database):

        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def listen(self, connection):
        """

        LISTENS TO SAMSARA EVENTS

        """
        connection.autocommit = True

        cursor = connection.cursor()
        cursor.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        tables = cursor.fetchall()

        install_trigger_function(connection)
        
        for t in tables:
            install_trigger(connection, str(t[0]))
        register_event_channel(connection)

        try:
            print('listening to events...')
            while True:
                for evt in poll(connection):
                    simp_handler.handle_event(evt)

        except KeyboardInterrupt:
            print('user exit via ctrl-c; shutting down...')
            install_trigger_function(connection)

            for t in tables:
                uninstall_trigger(connection, str(t[0]))

            unregister_event_channel(connection)
            uninstall_trigger_function(connection)
            print('shutdown complete.')

    def close_connect(self, connection):

        """

        DISCONNECTS FROM SAMSARA

        """

        connection.close()

def main():

    l = listener(simp_config.psql_samsara["host"], simp_config.psql_samsara["user"], simp_config.psql_samsara["password"], simp_config.psql_samsara["database"])
    
    try:
            connection = psycopg2.connect(database=l.database, user=l.user, password=l.password, host=l.host)
            print("success! welcome to samsara!")

    except:
        print("sorry couldn't connect to samsara")

    l.listen(connection)
    l.close_connect(connection)

if __name__ == "__main__":

    main()