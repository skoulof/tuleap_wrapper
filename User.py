from tuleap_wrapper.Fields import *
from tuleap_wrapper import tuleap_endpoint as tue
from typing import Self

class User:
    __tuleap_endpoint = tue.TuleapEndpoint()
    id = None
    real_name = None
    username = None
    email = None
    raw_fields = None

    def __init__(self, id=None, raw_fields=None):
        self.__id = id
        self.__raw_fields = raw_fields

        if not raw_fields:
            self.__raw_fields = dict()

    @classmethod
    def from_json(cls, jsonData) -> Self:

        new_user = cls(raw_fields=jsonData)

        new_user.id = jsonData["id"]
        new_user.real_name = jsonData["real_name"]
        new_user.username = jsonData["username"]
        new_user.email = jsonData["email"]

        return new_user

    @classmethod
    def from_id(cls, id) -> Self:
        json_user = cls.__tuleap_endpoint.get_user_by_id(id)
        return cls.from_json(json_user)


    def get_field(self, fieldSlug) -> Field:
        if not fieldSlug in self.__raw_fields.keys():
            print("Requested field " + fieldSlug + " not found")
        return self.__raw_fields[fieldSlug]

    def get_fields(self):
        return self.__raw_fields

    def get_avail_fields(self):
        return self.__raw_fields.keys()

    def is_field(self, fieldSlug) -> bool:
        return fieldSlug in self.__raw_fields.keys()
