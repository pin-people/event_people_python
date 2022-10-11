"""
    Wrap all logic of an event, whenever you receive or want to send

"""
import json
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

    def __init__(self, name, body):
         self.name = self.__fix_name__(name)
         self.__generate_header__()
         if body and "schema_version" in body:
            self.header.schema_version = body['schema_version']
         self.body = json.load(body)

    def __generate_header__(self, appName):
        resource, origin, action, destination = self.name.split(".")
        self.header = Header(app=Config.APP_NAME ,resource=resource, origin=origin, action=action, destination=destination)

    def __fix_name__(self, name):
        if len(name.split('.')) < 3:
            raise ValueError("pattern argument error in event's name")

        return f'{name}.all' if len(name.split('.')) == 3 else name

    def payload(self):
       return json.dumps({"header": str(self.header), "body": str(self.body)})
