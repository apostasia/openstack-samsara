from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client

from novaclient import client as nova_client

from samsara.common.credentials import get_admin_creds

def get_nova_auth():
    creds = get_nova_creds()
    auth = keystone_client.Password(**creds)
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2", session=sess)
    return nova

def get_admin_auth():
    creds = get_admin_creds()
    auth = v3.Password(auth_url=creds["auth_url"],
                   username=creds["username"],
                   password=creds["password"],
                   project_name=creds["project_name"],
                   user_domain_name=creds["user_domain_name"],
                   project_domain_name=creds["project_domain_name"])
    return auth

def get_session(auth):
    sess = session.Session(auth=auth)
    return sess

def get_admin_session():
    admin_auth = get_admin_auth()
    admin_session = get_session(admin_auth)
    return admin_session
