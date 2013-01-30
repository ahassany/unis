"""
Main Periscope Application
"""
import pymongo
import motor
from tornado import gen
import tornado.web
import tornado.ioloop
import json
import functools
import socket
from tornado.options import define
from tornado.options import options

from tornado.httpclient import AsyncHTTPClient

# before this import 'periscope' path name is NOT as defined!
import settings
from periscope.handlers import MIME
from settings import SCHEMAS
from periscope.db import DBLayerFactory
from periscope.utils import load_class
from periscope.models.unis import register_urn

# default port
define("port", default=8888, help="run on the given port", type=int)
define("address", default="0.0.0.0", help="default binding IP address",
       type=str)


class PeriscopeApplication(tornado.web.Application):
    """Defines Periscope Application."""

    def get_db_layer(self, collection_name, id_field_name,
                     timestamp_field_name, is_capped_collection,
                     capped_collection_size):
        """
        Creates DBLayer instance.
        """
        if collection_name is None:
            return None

        # Initialize the capped collection, if necessary!
        if is_capped_collection and \
                collection_name not in self.sync_db.collection_names():
            self.sync_db.create_collection(collection_name,
                            capped=True,
                            size=capped_collection_size,
                            autoIndexId=False)

        # Make indexes if the collection is not capped
        if id_field_name != timestamp_field_name:
            index = [(id_field_name, 1), (timestamp_field_name, -1)]
            self.sync_db[collection_name].ensure_index(index, unique=True)

        # Prepare the DBLayer
        db_layer = DBLayerFactory.new_dblayer(self.async_db,
                                              collection_name,
                                              is_capped_collection,
                                              id_field_name,
                                              timestamp_field_name)
        return db_layer

    def make_resource_handler(self, name,
                              pattern,
                              base_url,
                              handler_class,
                              model_class,
                              collection_name,
                              schema,
                              is_capped_collection,
                              capped_collection_size,
                              id_field_name,
                              timestamp_field_name,
                              allow_get,
                              allow_post,
                              allow_put,
                              allow_delete,
                              accepted_mime,
                              content_types_mime,
                              **kwargs):
        """
        Creates HTTP Request handler.

        :Parameters:
          - `name`: the name of the URL handler to be used with reverse_url.
          - `pattern: For example "/ports$" or "/ports/(?P<res_id>[^\/]*)$".
            The final URL of the resource is `base_url` + `pattern`.
          - `base_url`: see pattern
          - `handler_class`: The class handling this request.
            Must inherit `tornado.web.RequestHanlder`
          - `model_class`: Database model class for this resource (if any).
          - `collection_name`: The name of the database collection storing
            this resource.
          - `schema`: Schemas fot this resource in the form:
            "{MIME_TYPE: SCHEMA}"
          - `is_capped_collection`: If true the database collection is capped.
          - `capped_collection_size`: The size of the capped
            collection (if applicable)
          - `id_field_name`: name of the identifier field
          - `timestamp_field_name`: name of the timestampe field
          - `allow_get`: allow HTTP GET (True or False)
          - `allow_post`: allow HTTP POST (True or False)
          - `allow_put`: allow HTTP PUT (True or False)
          - `allow_delete`: allow HTTP DELETE (True or False)
          - `accepted_mime`: list of accepted MIME types
          - `content_types_mime`: List of Content types that can be returned
            to the user
          - `kwargs`: additional handler specific arguments
        """
        # Load classes
        if type(handler_class) in [str, unicode]:
            handler_class = load_class(handler_class)
        if type(model_class) in [str, unicode]:
            model_class = load_class(model_class)

        # Prepare the DBlayer
        db_layer = self.get_db_layer(collection_name,
                        id_field_name, timestamp_field_name,
                        is_capped_collection, capped_collection_size)

        # Make the handler
        handler = (
            tornado.web.URLSpec(base_url + pattern, handler_class,
                                dict(
                                    dblayer=db_layer,
                                    Id=id_field_name,
                                    timestamp=timestamp_field_name,
                                    base_url=base_url + pattern,
                                    allow_delete=allow_delete,
                                    schemas_single=schema,
                                    model_class=model_class,
                                    **kwargs),
                                name=name))
        return handler

    def _make_main_handler(self, name, pattern, base_url, handler_class,
                           resources):
        if type(handler_class) in [str, unicode]:
            handler_class = load_class(handler_class)
        main_handler = (
            tornado.web.URLSpec(base_url + pattern, handler_class,
                                dict(
                                    resources=resources,
                                    base_url=base_url + pattern,
                                ),
                                name=name))
        return main_handler

    def MS_registered(self, response):
        """A callback if MS is registered"""
        #TODO: This is a hack and should be updated.
        if response.error:
            print ("Couldn't start MS: ERROR", response.error)
            import sys
            sys.exit()
        else:
            body = json.loads(response.body)

    def __init__(self):
        self._async_db = None
        self._sync_db = None
        handlers = []

        for res in settings.Resources:
            handlers.append(
                self.make_resource_handler(**settings.Resources[res]))

        handlers.append(self._make_main_handler(**settings.main_handler_settings))
        tornado.web.Application.__init__(self, handlers,
                    default_host="localhost", **settings.APP_SETTINGS)        
        
        if settings.MS_ENABLE is True:
            callback = functools.partial(self.MS_registered)
            service = {
                       u"id": "ms_" + socket.gethostname(),
                       "\$schema": unicode(SCHEMAS["service"]),
                       "accessPoint": "http://%s:8888/" % socket.gethostname(),
                       "name": "ms_" + socket.gethostname(),
                       "status": "ON",
                       "serviceType": "ps:tools:ms",
                       "ttl": 1000,
                       #u"description": u"sample MS service",
                       "runningOn": {
                                      "href": "%s/nodes/%s"% (settings.UNIS_URL, socket.gethostname()),
                                      "rel": "full"
                                      },
                       "properties": {
                                       "configurations": {
                                                           "default_collection_size": 10000,
                                                           "max_collection_size": 20000
                                                           },
                                       "summary": {
                                                    "metadata": []
                                                    }
                                       }
                       }

            if 'localhost' in settings.UNIS_URL or "127.0.0.1" in settings.UNIS_URL:
                self.sync_db["services"].insert(service)
            else:
                service_url = settings.UNIS_URL + '/services'
                http_client = AsyncHTTPClient()
                content_type = MIME['PSJSON'] + \
                               '; profile=' + SCHEMAS['service']
                http_client.fetch(service_url,
                                  method="POST",
                                  body=json.dumps(service),
                                  headers={
                                        "Content-Type": content_type,
                                        "Cache-Control": "no-cache",
                                        "Accept": MIME['PSJSON'],
                                        "Connection": "close"},
                                  callback=callback)

    def register_urn(self, resource, callback):
        if not hasattr(self, '_register_urn'):
            urn_dblayer = DBLayerFactory.new_dblayer(self.async_db,
                "urn", False, "urn", "ts")
            self._register_urn = functools.partial(register_urn, urn_dblayer)
        return self._register_urn(resource, callback)
    
    def creat_pubsub(self):
        if 'pubsub' not in self.sync_db.collection_names():
            self.sync_db.create_collection('pubsub',
                capped=True, size=10000)
        self._pubsub = DBLayerFactory.new_dblayer(self.async_db, 'pubsub', capped=True)

    def publish(self, resource, callback, res_type=None):
        print "IN PUBLISH lkjsafhdlkasdhflkajsd"
        if not hasattr(self, '_pubsub'):
            self.creat_pubsub()
        tmp ={}
        tmp['id'] = resource['id']
        tmp['id'] = resource['id']
        res_type2 = resource['$schema'].rstrip('#').split('/')[-1]
        tmp['type'] = res_type or res_type2
        tmp['resource'] = dict(resource.to_mongoiter())
        print "Publishing", tmp
        self._pubsub.insert(tmp, callback)
    
    def subscribe(self, query, callback):
        if not hasattr(self, '_pubsub'):
            self.creat_pubsub()
        cursor = self._pubsub.find(query, tailable=True, await_data=True)
        cursor.each(callback=callback)
        

    @property
    def asyncmongo_db(self):
        """Returns a reference to asyncmongo DB connection."""
        import asyncmongo
        if not getattr(self, '_async_db', None):
            self._async_db = asyncmongo.Client(**settings.ASYNCMONGO_DB)
        return self._async_db

    @property
    def motor_db(self):
        """Returns a reference to motor DB connection."""
        if not getattr(self, '_async_db', None):
            conn = motor.MotorClient(**settings.MOTOR_DB).open_sync()
            self._async_db = conn[settings.DB_NAME]
        return self._async_db

    @property
    def async_db(self):
        #return self.asyncmongo_db
        return self.motor_db

    @property
    def sync_db(self):
        """Returns a reference to pymongo DB connection."""
        if not getattr(self, '_sync_db', None):
            conn = pymongo.Connection(**settings.SYNC_DB)
            self._sync_db = conn[settings.DB_NAME]
        return self._sync_db


def main():
    """Run periscope"""
    logger = settings.get_logger()
    logger.info('periscope.start')
    loop = tornado.ioloop.IOLoop.instance()
    #p = tornado.ioloop.PeriodicCallback(dot, 200, io_loop=loop)
    #p.start()
    # parse command line options
    tornado.options.parse_command_line()
    app = PeriscopeApplication()
    app.listen(options.port, address=options.address)
    loop.start()
    logger.info('periscope.end')


if __name__ == "__main__":
    main()
