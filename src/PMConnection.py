import os
import xmlrpc
from xmlrpc import client


class PMConnection:
    # rights in PM: Administration -> Administration -> Access Rights
    #               Extra Rights -> Contact Creation
    _server_url = os.getenv("SERVER_URL")
    _db_name = os.getenv("DB_NAME")
    _db_username = os.getenv("DB_USERNAME")
    _db_password = os.getenv("DB_PASSWORD")
    _model_name = "res.users"
    _common = None
    _db_user_id = None
    _models = None

    @classmethod
    def create_connection(cls):
        print("Connecting to DB...")
        cls._common = client.ServerProxy("%s/xmlrpc/2/common" % cls._server_url)
        cls._db_user_id = cls._common.authenticate(cls._db_name, cls._db_username, cls._db_password, {})
        cls._models = client.ServerProxy("%s/xmlrpc/2/object" % cls._server_url)
        _has_access = cls._models.execute_kw(cls._db_name, cls._db_user_id, cls._db_password,
                                             cls._model_name, "check_access_rights",
                                             ["write"], {"raise_exception": False})
        _has_access_partner = cls._models.execute_kw(cls._db_name, cls._db_user_id, cls._db_password,
                                                     "res.partner", "check_access_rights",
                                                     ["write"], {"raise_exception": False})
        if False in [_has_access, _has_access_partner]:
            raise xmlrpc.client.Fault(4, "PM Telegram Bot does not have adequate access."
                                         "\nPM Telegram Bot needs to be a member of the following groups:\n"
                                         "\t- Administration/Access Rights\n"
                                         "\t- Extra Rights/Contact Creation\n\n"
                                         "Contact your administrator to request access.")
        print("Connection to DB successful.")

    @classmethod
    async def db_has_bot(cls):
        return cls._db_user_id

    @classmethod
    async def get_contacts_to_write(cls, search_domain: list):
        try:
            contact_to_write = cls._models.execute_kw(cls._db_name, cls._db_user_id, cls._db_password,
                                                      cls._model_name, "search_read",
                                                      [search_domain])
            return contact_to_write
        except Exception as ex:
            return ex

    @classmethod
    async def write_to_contact(cls, contact_to_write: int, write_data: dict):
        try:
            written = cls._models.execute_kw(cls._db_name, cls._db_user_id, cls._db_password,
                                             cls._model_name, "write",
                                             [contact_to_write, write_data])
            return written
        except Exception as ex:
            return ex
