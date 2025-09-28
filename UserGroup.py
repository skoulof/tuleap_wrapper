from tuleap_wrapper.Fields import *
from tuleap_wrapper import tuleap_endpoint as tue
from typing import Self

class UserGroup:
    __tuleap_endpoint = tue.TuleapEndpoint()

    def __init__(self, id:int, user_id_list=[]):
        self.__id :int = id
        self.__user_ids :List[int] = user_id_list
        self.__updated = False

        if not user_id_list:
            self.__user_ids = []

    @classmethod
    def from_json(cls, jsonData) -> Self:
        grp_id = jsonData["id"]
        return cls.from_id(grp_id=grp_id)

    @classmethod
    def from_id(cls, grp_id) -> Self:
        users_in_grp = cls.__tuleap_endpoint.get_users_in_group(grp_id)

        user_ids = [item['id'] for item in users_in_grp]
        new_grp = cls(id=grp_id, user_id_list=user_ids)
        return new_grp

    @property
    def user_ids(self):
        return self.__user_ids
    @user_ids.setter
    def user_ids(self, value: List[int]):
        self.__user_ids = value
        self.__updated = True

    @property
    def id(self):
        return self.__id

    def add_users(self, user_ids):
        if isinstance(user_ids, int):
            user_ids = [user_ids]

        for id in user_ids:
            if not id in self.__user_ids:
                self.__user_ids.append(id)
                self.__updated = True

    def remove_users(self, user_ids):
        if isinstance(user_ids, int):
            user_ids = [user_ids]

        for id in user_ids:
            if id in self.__user_ids:
                self.__user_ids.remove(id)
                self.__updated = True

    def update(self):
        if self.__updated:
            self.__tuleap_endpoint.set_users_in_group(self.id, user_ids=self.__user_ids)
