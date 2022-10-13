"""
    Wrap all logic of an event, whenever you receive or want to send

"""
import json
import os
import ast
from pydantic import BaseModel
from typing import Dict

class Header(BaseModel):
    app: str
    resource: str
    origin: str
    action: str
    destination: str = 'all'
    schema_version: float = 1.0

class Event(object):
    """
        This class represents the pattern routing key got message_
    """
    APP_NAME = os.environ['RABBIT_EVENT_PEOPLE_APP_NAME']

    def __init__(self, name, body, schema_version = 1.0):
        self.name = self.__fix_name__(name)
        self.__generate_header__()
        body_dict = body

        if type(body) != dict:
             body_dict = ast.literal_eval(body.decode('utf-8'))

        self.header.schema_version = schema_version

        self.body = body_dict if 'body' not in body_dict else body_dict['body']

    def __generate_header__(self):
        resource, origin, action, destination = self.name.split(".")
        self.header = Header(app=self.APP_NAME ,resource=resource, origin=origin, action=action, destination=destination)

    def __fix_name__(self, name):
        if len(name.split('.')) < 3:
            raise ValueError("pattern argument error in event's name")

        return f'{name}.all' if len(name.split('.')) == 3 else name

    def payload(self):
       return json.dumps({"header": str(self.header), "body": str(self.body)})
