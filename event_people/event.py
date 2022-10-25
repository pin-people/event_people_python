"""
    Wrap all logic of an event, whenever you receive or want to send

"""
import json
import os
import ast

class Header:

    def __init__(self, app, resource, origin, action, destination, schema_version=None):
        self.app = app
        self.resource = resource
        self.origin = origin
        self.action = action
        self.destination = destination
        self.schema_version = schema_version or 1.0

    def __str__(self):
        return f'{self.app}.{self.resource}.{self.origin}.{self.action}.{self.destination}.{self.schema_version}'


class Event(object):
    """
        This class represents the pattern routing key got message_
    """
    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']

    def __init__(self, name, body, schema_version = 1.0):
        self.name = self.__fix_name__(name)
        self.__generate_header__(schema_version)
        body_dict = body

        if not isinstance(body, dict):
            body_dict = ast.literal_eval(body.decode('utf-8'))

        self.header.schema_version = schema_version

        self.body = body_dict if 'body' not in body_dict else body_dict['body']


    def __generate_header__(self, schema_version):
        resource, origin, action, destination = self.name.split(".")
        self.header = Header(app=self.APP_NAME ,resource=resource, origin=origin, action=action, destination=destination, schema_version=schema_version)

    def __fix_name__(self, name):
        if len(name.split('.')) < 3:
            raise ValueError("pattern argument error in event's name")

        return f'{name}.all' if len(name.split('.')) == 3 else name

    def payload(self):
       return json.dumps({"headers": self.header.__dict__, "body": self.body})
