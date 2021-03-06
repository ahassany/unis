"""
General Perisocpe Settings.
"""
import ssl
import logging
import os
import sys
from netlogger import nllog
from tornado.options import define


######################################################################
# Setting up path names.
######################################################################
PERISCOPE_ROOT = os.path.dirname(os.path.abspath(__file__)) + os.sep
sys.path.append(os.path.dirname(os.path.dirname(PERISCOPE_ROOT)))
#SCHEMA_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache")
SCHEMA_CACHE_DIR = None

GCF_PATH = "/opt/gcf/src/"
sys.path.append(os.path.dirname(GCF_PATH))

AUTH_STORE_DIR = os.path.join(os.path.dirname(__file__), "abac")

JSON_SCHEMAS_ROOT = PERISCOPE_ROOT + "/schemas"

######################################################################
# Tornado settings.
######################################################################

ENABLE_SSL = False
SSL_OPTIONS = {
    'certfile': os.path.join(PERISCOPE_ROOT, "ssl/server.pem"),
    'keyfile': os.path.join(PERISCOPE_ROOT, "ssl/server.key"),
    'cert_reqs': ssl.CERT_REQUIRED,
    'ca_certs': os.path.join(PERISCOPE_ROOT, "ssl/genica.bundle")
}

######################################################################
# Measurement Store settings.
######################################################################
#UNIS_URL = "https://unis.incntre.iu.edu:8443"
UNIS_URL = "http://localhost:8888"
MS_ENABLE = True

MS_CLIENT_CERT = "/usr/local/etc/certs/ms_cert.pem"
MS_CLIENT_KEY = "/usr/local/etc/certs/ms_key.pem"
GEMINI_NODE_INFO = None


######################################################################
# Periscope Application settings.
######################################################################

# Enable GENI/ABAC auth support
ENABLE_AUTH = False

# Enable application wide debugging options
DEBUG = True

APP_SETTINGS = {
    'cookie_secret': "43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    'template_path': os.path.join(os.path.dirname(__file__), "templates/"),
    'static_path': os.path.join(os.path.dirname(__file__), "static/"),
    'xsrf_cookies': False,
    'autoescape': "xhtml_escape",
    'debug': DEBUG,
}

######################################################################
# Mongo Database settings
######################################################################
DB_NAME = "periscope_db"
DB_HOST = "127.0.0.1"
DB_PORT = 27017

# Asyncmongo specific connection configurations
ASYNC_DB = {
    'pool_id': DB_HOST + "_pool",
    'host': DB_HOST,
    'port': DB_PORT,
    'mincached': 1,
    'maxcached': 50,
    'maxconnections': 250,
    'dbname': DB_NAME,
}

# Pymonog specific connection configurations
SYNC_DB = {
    'host': DB_HOST,
    'port': DB_PORT,
}


######################################################################
# Netlogger settings
# (AH): This need to be refactored to more flexible settings
######################################################################
NETLOGGER_NAMESPACE = "periscope"


def config_logger():
    """Configures netlogger"""
    nllog.PROJECT_NAMESPACE = NETLOGGER_NAMESPACE
    #logging.setLoggerClass(nllog.PrettyBPLogger)
    logging.setLoggerClass(nllog.BPLogger)
    log = logging.getLogger(nllog.PROJECT_NAMESPACE)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    # set level
    if DEBUG:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                 nllog.TRACE)[3]
    else:
        log_level = (logging.WARN, logging.INFO, logging.DEBUG,
                 nllog.TRACE)[0]
    log.setLevel(log_level)


def get_logger(namespace=NETLOGGER_NAMESPACE):
    """Return logger object"""
    # Test if netlloger is initialized
    if nllog.PROJECT_NAMESPACE != NETLOGGER_NAMESPACE:
        config_logger()
    return nllog.get_logger(namespace)




######################################################################
# NetworkResource Handlers settings
######################################################################
MIME = {
    'HTML': 'text/html',
    'JSON': 'application/json',
    'PLAIN': 'text/plain',
    'SSE': 'text/event-stream',
    'PSJSON': 'application/perfsonar+json',
    'PSBSON': 'application/perfsonar+bson',
    'PSXML': 'application/perfsonar+xml',
}

SCHEMAS = {
    'networkresource': 'http://unis.incntre.iu.edu/schema/20120709/networkresource#',
    'node': 'http://unis.incntre.iu.edu/schema/20120709/node#',
    'domain': 'http://unis.incntre.iu.edu/schema/20120709/domain#',
    'port': 'http://unis.incntre.iu.edu/schema/20120709/port#',
    'link': 'http://unis.incntre.iu.edu/schema/20120709/link#',
    'path': 'http://unis.incntre.iu.edu/schema/20120709/path#',
    'network': 'http://unis.incntre.iu.edu/schema/20120709/network#',
    'topology': 'http://unis.incntre.iu.edu/schema/20120709/topology#',
    'service': 'http://unis.incntre.iu.edu/schema/20120709/service#',
    'blipp': 'http://unis.incntre.iu.edu/schema/20120709/blipp#',
    'metadata': 'http://unis.incntre.iu.edu/schema/20120709/metadata#',
    'data' : 'http://unis.incntre.iu.edu/schema/20120709/data#',
    'datum' : 'http://unis.incntre.iu.edu/schema/20120709/datum#',
    'measurement': 'http://unis.incntre.iu.edu/schema/20130416/measurement#',
}

# Default settings that apply to almost all network resources
# This is used to make writing `Resources` easier.
default_resource_settings= {
    "base_url": "", # For additional URL extension, e.g. /mynetwork/unis will make /ports like /mynetwork/unis/ports
    "handler_class": "periscope.handlers.NetworkResourceHandler", # The HTTP Request Handler class
    "is_capped_collection": False,
    "capped_collection_size": 0,
    "id_field_name": "id",
    "timestamp_field_name": "ts",
    "allow_get": True,
    "allow_post": True,
    "allow_put": True,
    "allow_delete": True,
    "accepted_mime": [MIME['SSE'], MIME['PSJSON']],
    "content_types_mime": [MIME['SSE'], MIME['PSJSON']]
}

links = dict(default_resource_settings.items() + \
        {
            "name": "links",
            "pattern": "/links$", # The regex used to match the handler in URI
            "model_class": "periscope.models.Link", # The name of the database collection
            "collection_name": "links",
            "schema": {MIME['PSJSON']: SCHEMAS["link"]}, # JSON Schema fot this resource
        }.items()
)
link = dict(default_resource_settings.items() + \
        {
            "name": "link",
            "pattern": "/links/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Link",
            "collection_name": "links",
            "schema": {MIME['PSJSON']: SCHEMAS["link"]},
        }.items()
)
ports = dict(default_resource_settings.items() + \
        {
            "name": "ports",
            "pattern": "/ports$",
            "model_class": "periscope.models.Port",
            "collection_name": "ports",
            "schema": {MIME['PSJSON']: SCHEMAS["port"]},
        }.items()
)
port = dict(default_resource_settings.items() + \
        {
            "name": "port",
            "pattern": "/ports/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Port",
            "collection_name": "ports",
            "schema": {MIME['PSJSON']: SCHEMAS["port"]},
        }.items()
)
nodes = dict(default_resource_settings.items() + \
        {
            "name": "nodes",
            "pattern": "/nodes$",
            "model_class": "periscope.models.Node",
            "collection_name": "nodes",
            "schema": {MIME['PSJSON']: SCHEMAS["node"]},
        }.items()
)
node = dict(default_resource_settings.items() + \
        {
            "name": "node",
            "pattern": "/nodes/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Node",
            "collection_name": "nodes",
            "schema": {MIME['PSJSON']: SCHEMAS["node"]},
        }.items()
)
services = dict(default_resource_settings.items() + \
        {
            "name": "services",
            "pattern": "/services$",
            "model_class": "periscope.models.Service",
            "collection_name": "services",
            "schema": {MIME['PSJSON']: SCHEMAS["service"]},
        }.items()
)
service = dict(default_resource_settings.items() + \
        {
            "name": "service",
            "pattern": "/services/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Service",
            "collection_name": "services",
            "schema": {MIME['PSJSON']: SCHEMAS["service"]},
        }.items()
)
paths = dict(default_resource_settings.items() + \
        {
            "name": "paths",
            "pattern": "/paths$",
            "model_class": "periscope.models.Path",
            "collection_name": "paths",
            "schema": {MIME['PSJSON']: SCHEMAS["path"]},
        }.items()
)
path = dict(default_resource_settings.items() + \
        {
            "name": "path",
            "pattern": "/paths/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Path",
            "collection_name": "paths",
            "schema": {MIME['PSJSON']: SCHEMAS["path"]},
        }.items()
)
networks = dict(default_resource_settings.items() + \
        {
            "name": "networks",
            "pattern": "/networks$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Network",
            "collection_name": "networks",
            "schema": {MIME['PSJSON']: SCHEMAS["network"]},
            "collections": {},
        }.items()
)
network = dict(default_resource_settings.items() + \
        {
            "name": "network",
            "pattern": "/networks/(?P<res_id>[^\/]*)$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Network",
            "collection_name": "networks",
            "schema": {MIME['PSJSON']: SCHEMAS["network"]},
            "collections": {},
        }.items()
)
domains = dict(default_resource_settings.items() + \
        {
            "name": "domains",
            "pattern": "/domains$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Domain",
            "collection_name": "domains",
            "schema": {MIME['PSJSON']: SCHEMAS["domain"]},
            "collections": {},
        }.items()
)
domain = dict(default_resource_settings.items() + \
        {
            "name": "domain",
            "pattern": "/domains/(?P<res_id>[^\/]*)$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Domain",
            "collection_name": "domains",
            "schema": {MIME['PSJSON']: SCHEMAS["domain"]},
            "collections": {},
        }.items()
)
topologies = dict(default_resource_settings.items() + \
        {
            "name": "topologies",
            "pattern": "/topologies$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Topology",
            "collection_name": "topologies",
            "schema": {MIME['PSJSON']: SCHEMAS["topology"]},
            "collections": {},
        }.items()
)
topology = dict(default_resource_settings.items() + \
        {
            "name": "topology",
            "pattern": "/topologies/(?P<res_id>[^\/]*)$",
            "handler_class": "periscope.handlers.CollectionHandler",
            "model_class": "periscope.models.Topology",
            "collection_name": "topologies",
            "schema": {MIME['PSJSON']: SCHEMAS["topology"]},
            "collections": {},
        }.items()
)

metadatas = dict(default_resource_settings.items() + \
        {
            "name": "metadatas",
            "pattern": "/metadata$", 
            "model_class": "periscope.models.Metadata",
            "collection_name": "metadata",
            "schema": {MIME['PSJSON']: SCHEMAS["metadata"]},
        }.items()
)
metadata = dict(default_resource_settings.items() + \
        {
            "name": "metadata",
            "pattern": "/metadata/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Metadata",
            "collection_name": "metadata",
            "schema": {MIME['PSJSON']: SCHEMAS["metadata"]},
        }.items()
)

events = dict(default_resource_settings.items() + \
        {
            "name": "events",
            "pattern": "/events$", 
            "handler_class" : "periscope.handlers.EventsHandler",
            "model_class": "periscope.models.Event",
            "collection_name": "events_cache",
            "schema": {MIME['PSJSON']: SCHEMAS["datum"]},
        }.items()
)

event = dict(default_resource_settings.items() + \
        {
            "name": "event",
            "pattern": "/events/(?P<res_id>[^\/]*)$",
            "handler_class" : "periscope.handlers.EventsHandler",
            "model_class": "periscope.models.Event",
            "collection_name": None,
            "schema": {MIME['PSJSON']: SCHEMAS["datum"]},
        }.items()
)

datas = dict(default_resource_settings.items() + \
        {
            "name": "datas",
            "pattern": "/data$", 
            "handler_class" : "periscope.handlers.DataHandler",
            "model_class": "periscope.models.Data",
            "collection_name": None,
            "schema": {MIME['PSJSON']: SCHEMAS["data"]},
        }.items()
)

data = dict(default_resource_settings.items() + \
        {
            "name": "data",
            "pattern": "/data/(?P<res_id>[^\/]*)$",
            "handler_class" : "periscope.handlers.DataHandler",
            "model_class": "periscope.models.Data",
            "collection_name": None,
            "schema": {MIME['PSJSON']: SCHEMAS["data"]},
        }.items()
)

measurements = dict(default_resource_settings.items() + \
        {
            "name": "measurements",
            "pattern": "/measurements$",
            "model_class": "periscope.models.Measurement",
            "collection_name": "measurements",
            "schema": {MIME['PSJSON']: SCHEMAS["measurement"]},
        }.items()
)
measurement = dict(default_resource_settings.items() + \
        {
            "name": "measurement",
            "pattern": "/measurements/(?P<res_id>[^\/]*)$",
            "model_class": "periscope.models.Measurement",
            "collection_name": "measurements",
            "schema": {MIME['PSJSON']: SCHEMAS["measurement"]},
        }.items()
)

collections = {
    "links": link,
    "ports": port,
    "nodes": node,
    "services": service,
    "paths": path,
    "networks": network,
    "domains": domain,
    "topologies": topology,
    "measurements": measurement,
}

topologies["collections"] = collections
topology["collections"] = collections
domains["collections"] = collections
domain["collections"] = collections
networks["collections"] = collections
network["collections"] = collections

Resources = {
    "links": links,
    "link": link,
    "ports": ports,
    "port": port,
    "nodes": nodes,
    "node": node,
    "services": services,
    "service": service,
    "paths": paths,
    "path": path,
    "networks": networks,
    "network": network,
    "domains": domains,
    "domain": domain,
    "topologies": topologies,
    "topology": topology,
    "metadatas": metadatas,
    "metadata": metadata,
    "events" : events,
    "event" : event,
    "data" : data,
    "datas" : datas,
    "measurements": measurements,
    "measurement" : measurement,
}

main_handler_settings = {
    "resources": ["links", "ports", "nodes", "services", "paths",
        "networks", "domains", "topologies", "events", "datas", "metadatas", "measurements"],
    "name": "main",
    "base_url": "",
    "pattern": "/$",
    "handler_class": "periscope.handlers.MainHandler",
}

######################################################################
# PRE/POST content processing module definitions.
######################################################################

PP_MODULES = [('periscope.gemini', 'Gemini')]
#PP_MODULES = []

# Settings for the GEMINI-specific authentication handlers
auth_user_settings= {
    "base_url": "",
    "handler_class": "periscope.gemini.AuthUserCredHandler",
    "name": "cred_geniuser",
    "pattern": "/credentials/geniuser",
    "schema": [MIME['PLAIN']]
}

auth_slice_settings= {
    "base_url": "",
    "handler_class": "periscope.gemini.AuthSliceCredHandler",
    "name": "cred_genislice",
    "pattern": "/credentials/genislice",
    "schema": [MIME['PLAIN']]
}

AuthResources = {
    "cred_geniuser": auth_user_settings,
    "cred_genislice": auth_slice_settings
}


if GEMINI_NODE_INFO is not None:
    logger = get_logger()
    nconf = {}
    with open(GEMINI_NODE_INFO, 'r') as cfile:
        for line in cfile:
            name, var = line.partition("=")[::2]
            nconf[name.strip()] = str(var).rstrip()

        try:
            AUTH_UUID = nconf['auth_uuid']
        except Exception as e:
            AUTH_UUID = None
            logger.warn("read_settings", msg="Could not find auth_uuid in node configuration")
else:
    AUTH_UUID = None

try:
    from M2Crypto import X509
    SERVER_CERT_FINGERPRINT = X509.load_cert(SSL_OPTIONS['certfile'], X509.FORMAT_PEM).get_fingerprint('sha1')
except Exception as e:
    SERVER_CERT_FINGERPRINT = ''
    logger = get_logger()
    logger.warn("read_settings", msg="Could not open SSL CERTFILE: %s" % e)
