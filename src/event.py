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
    destiny: str = 'all'
    schema_version: float = 1.0


class Body(BaseModel):
    message: Dict

class Event(object):
    """
        This class represents the pattern routing key got message_
    """

    def __init__(self, name: str, body: dict, appName: str = 'event_people_app') -> None:
         self.name = self.__fix_name__(name)
         self.__generate_header__(appName)
         if body and "schema_version" in body:
            self.header.schema_version = body['schema_version']
         self.body = Body(message=body)

    def __generate_header__(self, appName):
        resource, origin, action, destiny = self.name.split(".")
        self.header = Header(app=appName,resource=resource, origin=origin, action=action, destiny=destiny)

    def __fix_name__(self, name):
        if len(name.split('.')) < 3:
            raise ValueError("pattern argument error in event's name")

        return f'{name}.all' if  3 <= len(name.split('.')) < 4 else name

    def payload(self):
       return json.dumps({"header": dict(self.header), "body": dict(self.body)})