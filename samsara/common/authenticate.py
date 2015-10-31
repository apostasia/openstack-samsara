from keystoneclient.auth.identity import v3 as keystone_client
from keystoneclient import session
from novaclient import client as nova_client

from credentials import get_nova_creds

def get_nova_auth():
    creds = get_nova_creds()
    auth = keystone_client.Password(**creds)
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2", session=sess)
    return nova 