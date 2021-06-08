from flask import jsonify
import simp_agent
import samsara_agent

def handle_event(event):
    """

    EVENT HANDLER

    """
    print('new event: {}'.format(event))

    if event.type == "INSERT":
        insert(event)
    elif event.type == "UPDATE":
        update(event)
    elif event.type == "DELETE":
        delete(event)
    else:
        print("event not found")

def insert(event):
    """

    INSERT EVENT

    """
    print("this is a insert event!")
    insert_actions(event)

def update(event):
    """

    UPDATE EVENT

    """
    print("this is a update event!")
    update_actions(event)


def delete(event):
    """

    DELETE EVENT

    """
    print("this is a delete event!")


def insert_actions(event):
    """

    INSERT ACTIONS

    """
    print("getting action table!")

    if (event.table_name == 'cell_situation'):
        cell_situation_insert_action(event.table_name, event.row_id)
    elif (event.table_name == 'migration_events'):
        migration_events_insert_action(event.table_name, event.row_id)
    elif (event.table_name == 'host_resources_usage'):
        host_resources_usage_insert_action(event.table_name, event.row_id)
    elif (event.table_name == 'host_situation'):
        host_situation_insert_action(event.table_name, event.row_id)


def update_actions(event):
    """

    UPDATE ACTIONS

    """
    print("getting action table!")

    if (event.table_name == 'cell_situation'):
        cell_situation_update_action(event.table_id, event.row_id)
    elif (event.table_name == 'migration_events'):
        migration_events_update_action(event.table_id, event.row_id)
    elif (event.table_name == 'host_situation'):
        host_situation_update_action(event.table_name, event.row_id)
    elif (event.table_name == 'host_resources_usage'):
        host_resources_usage_update_action(event.table_name, event.row_id)


def cell_situation_update_action(table_name, row_id):
    """

    UPDATE ACTION INTO CELL SITUATION

    """
    print("handling update action for cell_situation!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)
    simp_data = simp_agent.get_last_cell_situation_row()

    simp_agent.insert_into_cell_situation(controller_data)


def cell_situation_insert_action(table_name, row_id):
    """

    INSERT ACTION INTO CELL SITUATION

    """
    print("handling insert action for cell_situation!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_cell_situation(controller_data)

    host_situation_data = samsara_agent.get_last_row('host_situation')
    simp_agent.insert_into_host_situation(host_situation_data)

    migration_events_data = samsara_agent.get_last_row('migration_events')
    simp_agent.insert_into_migration_events(migration_events_data)


def migration_events_insert_action(table_name, row_id):
    """

    INSERT ACTION INTO MIGRATION EVENTS

    """
    print("handling insert action in migration_events!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_migration_events(controller_data)


def migration_events_update_action(table_name, row_id):
    """

    UPDATE ACTION INTO MIGRATION EVENTS

    """
    print("handling update action in migration_events!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_migration_events(controller_data)


def host_resources_usage_update_action(table_name, row_id):
    """

    UPDATE ACTION INTO HOST RESOURCES USAGE

    """
    print("handling update action in host_resources_usage!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_host_resources_usage(controller_data)


def host_resources_usage_insert_action(table_name, row_id):
    """

    INSERT ACTION INTO HOST RESOURCES USAGE

    """
    print("handling insert action in host_resources_usage!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_host_resources_usage(controller_data)


def host_situation_update_action(table_name, row_id):
    """

    UPDATE ACTION INTO HOST SITUATION

    """
    print("handling update action for host_situation!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_host_situation(controller_data)


def host_situation_insert_action(table_name, row_id):
    """

    UPDATE ACTION INTO HOST SITUATION

    """
    print("handling insert action for host_situation!")
    controller_data = samsara_agent.get_event_row(table_name, row_id)

    simp_agent.insert_into_host_situation(controller_data)