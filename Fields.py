from enum import Enum
from .utils import iso_to_datetime, datetime_to_iso
from datetime import datetime
from typing import List, Self
import re
import copy


class Field_type():
    NONE = "none"
    STRING = "string"
    TEXT = "text"
    BUTTONS = "buttons"
    ARTLINKS = "art_link"
    FILES = "file"
    MSB = "msb"
    SB = "sb"
    CB = "cb"
    RB = "rb"
    DATE = "date"
    SUBON = "subon"
    LUD = "lud"
    FLOAT = "float"
    USER = "user"
    USERS = "users"
    SUBBY = "subby"
    LUBY = "luby"

class Field:
    def __init__(self, id=None, slug=None, fieldType=Field_type.NONE):
        self.__id= id
        self.__slug = slug
        self._updated = False
        self._dependent = False
        self.__fieldType = fieldType

    @property
    def id(self):
        return self.__id
    @id.setter
    def id(self, value:int):
        #TODO: Should we update ?
        self.__id = value

    @property
    def slug(self):
        return self.__slug
    @slug.setter
    def slug(self, value:str):
        self.__slug = value

    @property
    def updated(self):
        return self._updated
    @updated.setter
    def updated(self, value:bool):
        self._updated = value

    @property
    def dependent(self):
        return self._dependent
    @dependent.setter
    def dependent(self, value:bool):
        self._dependent = value

    @property
    def fieldType(self) -> Field_type:
        return self.__fieldType

    def toJson(self):
        return {}

class Field_string(Field):
    def __init__(self, id=None, slug=None, value=None, fieldType=Field_type.STRING):
        """
            Initialize a new instance of the class.

            Parameters:
            id (int): A positive integer representing the identifier. Default is None.
            slug (str): A string representing the slug. Default is None.
            value (str): A string representing the value. Default is None.
        """

        super().__init__(id, slug, fieldType)
        self.__value = value

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value:str):
        self.updated = True
        self.__value = value

    def toJson(self):
        return {"field_id":self.id, "value":self.value}

class Field_text(Field_string):
    class Tformat():
        CHAR = "char"
        TEXT = "text"
        HTML = "html"
        MDWN = "markdown"

    def __init__(self, id=None, slug=None, value=None, t_format=Tformat.TEXT):
        super().__init__(id, slug, value, Field_type.TEXT)
        self.__tFormat = t_format

    @property
    def tFormat(self):
        return self.__tFormat
    @tFormat.setter
    def tFormat(self, value:str):
        self.updated = True
        self.__tFormat = value

    def toJson(self):
        return {"field_id":self.id, "value":self.value, "format":self.tFormat}

class Field_buttons(Field_text):
    class Alignment:
        CENTERED = "center"
        LEFT = "left"
        RIGHT = "right"

    BT_SEARCH_PATTERN = r'<a.*?>.*?</a>'
    ALIGN_SEARCH_PATTERN = r'<div style=".*?text-align:\s*([^;]+).*?"'

    def __init__(self, id=None, slug=None, value=None, t_format=Field_text.Tformat.HTML):
        super().__init__(id, slug, value, Field_type.BUTTONS)
        self.__buttonList = []
        self.__alignment = Field_buttons.Alignment.LEFT

        if value:
            links = re.findall(self.BT_SEARCH_PATTERN, value)
            alignment = re.search(self.ALIGN_SEARCH_PATTERN, value)
            if alignment:
                self.__alignment = alignment.group(1).strip()
            if len(links) > 0:
                self.__buttonList = links
            self.generate_buttons()

    def generate_buttons(self):
        result_string = ""
        result_string += f'<div style="text-align: {self.__alignment}">' + '\n'
        for item in self.__buttonList:
            result_string += item + '\n'
        result_string += "</div>"

        self.value = result_string

    def get_buttons(self):
        return self.__buttonList

    def add_button(self, html_button):
        self.__buttonList.append(html_button)
        self.generate_buttons()
        self.updated = True

    def set_alignment(self, alignment:Alignment):
        self.__alignment = alignment
        self.generate_buttons()
        self.updated = True

    def get_alignment(self) -> Alignment:
        return self.__alignment

    def clear_buttons(self):
        self.__buttonList = []
        self.__alignment = self.Alignment.LEFT
        self.generate_buttons()
        self.updated = True

class Field_artLinks(Field):
    class ArtLink:
        class Direction():
            FORWARD = "forward"
            REVERSE = "reverse"

        class Relation():
            NONE = ""
            CHILD = "_is_child"
            COVERED_BY = "_covered_by"
            CANCELED_BY = "canceled_by"
            DUPLICATE = "duplicate"
            FIXED_IN = "fixed_in"
            IS_AFTER = "is_after"
            OPEN_SOFTWARE_RIGHTS = "open_software_rights"
            RELATE_TO = "rel_to"

        def __init__(self, id_artifact, id_tracker=None, direction=Direction.FORWARD, relation=Relation.NONE, isNew=False):
            self.__id_artifact = id_artifact
            self.__id_tracker = id_tracker
            self.__direction = direction
            self.__relation = relation
            self.__updated  =  isNew
            if not relation:
                self.__relation = Field_artLinks.ArtLink.Relation.NONE

        @property
        def id_artifact(self):
            return self.__id_artifact
        @id_artifact.setter
        def id_artifact(self, value:int):
            self.__id_artifact = value
            self.__updated = True

        @property
        def id_tracker(self):
            return self.__id_tracker
        @id_tracker.setter
        def id_tracker(self, value:int):
            self.__id_tracker = value
            self.__updated = True

        @property
        def direction(self):
            return self.__direction
        @direction.setter
        def direction(self, value:str):
            self.__direction = value
            self.__updated = True

        @property
        def relation(self):
            return self.__relation
        @relation.setter
        def relation(self, value:str):
            self.__relation = value
            self.__updated = True

        @property
        def updated(self):
            return self.__updated
        @updated.setter
        def updated(self, value:bool):
            self.__updated = value

        def __str__(self):
            return "{}-{}-{}".format(self.id_artifact, self.direction, self.relation)
        def __repr__(self):
            #TODO: FIXME
            return "Linked_artifact({},{},{})".format(self.__id_artifact, self.__direction, self.__relation)

        def __eq__(self, value:Self):
            if type(self) == type(value):
                return (self.__id_artifact == value.__id_artifact and
                        self.__direction == value.__direction and
                        self.__relation == value.__relation)
            elif isinstance(value, int):
                return self.__id_artifact == value
            else:
                return False

        def json(self):
            return {"id":self.__id_artifact, "direction":self.__direction, "type":self.__relation}

    def __init__(self, id=None, slug=None, value=[]):
        super().__init__(id, slug, Field_type.ARTLINKS)
        self.__artLinks:List[Field_artLinks.ArtLink] = value

    @property
    def artLinks(self):
        return self.__artLinks
    @artLinks.setter
    def artLinks(self, links_list:List[ArtLink]):
        self.__artLinks = links_list
        self.updated = True

    @property
    def get_link(self, index):
        return self.artLinks[index]

    @property
    def updated(self):
        result = self._updated
        for iLink in self.__artLinks:
            if iLink.updated:
                result = True

        return result
    @updated.setter
    def updated(self, value:bool):
        self._updated = value

    def add_link(self, link:ArtLink):
        if link not in [item for item in self.__artLinks]:
            # Prevent multiple link of different type
            self.remove_link(artifact_id=link.id_artifact)
            indep_link = copy.copy(link)
            indep_link.updated = True
            self.__artLinks.append(indep_link)

    def add_links(self, links:List[ArtLink]):
        for link in links:
            self.add_link(link)

    def remove_link(self, artLink:ArtLink=None, artifact_id:int=None):
        if artLink and (artLink in self.artLinks):
            self.__artLinks.remove(artLink)
            self.updated = True
        elif artifact_id:
            for link in self.__artLinks:
                if link.id_artifact == artifact_id:
                    self.remove_link(link)

    def clear_links(self):
        self.__artLinks.clear()
        self.updated = True

    def from_tracker_id(self, tracker_id:int) -> list[ArtLink]:
        result = []
        for link in self.artLinks:
            if (link.id_tracker == tracker_id):
                result.append(link)
        return result

    def print_links(self):
        for link in self.artLinks:
            print('-->',str(link))

    def toJson(self):
        return {"field_id":self.id, "all_links":[item.json() for item in self.__artLinks]}

class Field_files(Field):
    class File:
        def __init__(self, id=None, name=None, description=None, html_url=None):
            self.__id = id
            self.__name = name
            self.__description = description
            self.__html_url = html_url

        @classmethod
        def from_json(cls, json_data):
            return cls(id=json_data["id"], name=json_data["name"], description=json_data["description"], html_url=json_data["html_url"])

        @property
        def html_url(self):
            return self.__html_url

        @property
        def id(self):
            return self.__id

        @property
        def name(self):
            return self.__name

        @property
        def description(self):
            return self.__description

    def __init__(self, id=None, slug=None, file_descriptions=None):
        super().__init__(id, slug, Field_type.FILES)
        self.__files:list[Field_files.File] = []

        if file_descriptions:
            for item in file_descriptions:
                self.__files.append(self.File.from_json(item))

    @property
    def files(self):
        return self.__files
    #pas de beosin de setter identifié, si on a besoin d'ajouter des files à un artefact il faudra passer par une fonction add_file...

    def downLoad(self, path):
        pass

    def storeOnIsiFish(self, DFS, svc_username, svc_password, path):
        pass

    def remove_file(self, fileToRemove:File):
        if fileToRemove in self.files:
            self.__files.remove(fileToRemove)
            self.updated = True

    def clear_links(self):
        self.__files.clear
        self.updated = True

    def __str__(self):
            return "{}-{}-{}".format(self.id_artefact, self.name, self.description)

    def toJson(self):
        return {"field_id":self.id,"value":[item.id for item in self.files]}

class Field_msb(Field):
    class Selectable_item:
        def __init__(self, id:int, label:str):
            self.__id = id
            self.__label = label

        @property
        def id(self):
            return self.__id
        @id.setter
        def id(self, id):
            self.__id = id

        @property
        def label(self):
            return self.__label
        @label.setter
        def label(self, label):
            self.__label = label

        def __eq__(self, value:Self):
            if type(self) == type(value):
                return (self.__id == value.__id and
                        self.__label == value.__label)
            else:
                return False

    EMPTY_FIELD_VID = 100
    EMPTY_SELECTABLE_ITEM = Selectable_item(id=EMPTY_FIELD_VID, label="")
    def __init__(self, id, slug, field_struct, values=[], fieldType=Field_type.MSB):
        super().__init__(id, slug, fieldType)
        self.__field_struct = field_struct
        self._values:list[Field_msb.Selectable_item] = [self.EMPTY_SELECTABLE_ITEM]
        self._label_to_id = {field['label']: field['id'] for field in field_struct["values"]}
        self._label_to_id[""] = self.EMPTY_FIELD_VID
        self._id_to_label = {field['id']: field['label'] for field in field_struct["values"]}
        self._id_to_label[self.EMPTY_FIELD_VID] = ""
        self._legal = True

        if values:
            for item in values:
                if item["id"] == None:
                    pass
                else:
                    if("label" in item.keys()):
                        self._values.append(Field_msb.Selectable_item(item["id"], item["label"]))
                    else:
                        self._values.append(Field_msb.Selectable_item(item["id"], item["username"])) #TODO: FIXME

        if not self.isEmpty():
            self._values.remove(self.EMPTY_SELECTABLE_ITEM)

        def __str__(self):
            return "id:{}; label:{}".format(self.id, self.label)

    def add_selectable_item(self, inSelectableItem:Selectable_item):
        # Adding empty means clearing
        if (inSelectableItem == self.EMPTY_SELECTABLE_ITEM):
            self.clearValues()
            return

        if (self.EMPTY_SELECTABLE_ITEM in self._values):
            if (inSelectableItem == self.EMPTY_SELECTABLE_ITEM):
                return
            else:
                self._values.remove(self.EMPTY_SELECTABLE_ITEM)

        if inSelectableItem not in self._values:
            self._values.append(inSelectableItem)
            self.updated = True

    def add(self, id=None, label=None):
        if ((not id) and (not label)):
            return

        new_sb = None
        if id:
            new_sb = Field_msb.Selectable_item(id, self._id_to_label[id])
        elif label:
            new_sb = Field_msb.Selectable_item(self._label_to_id[label], label)

        self.add_selectable_item(new_sb)

    def add_list(self, id_list=None, label_list=None):
        if id_list:
            for id in id_list:
                self.add(id=id)
        elif label_list:
            for label in label_list:
                self.add(label=label)

    def remove(self, id=None, label=None):
        if id:
            self._values.remove(Field_msb.Selectable_item(id, self.__id_to_label[id]))
        elif label:
            self._values.remove(Field_msb.Selectable_item(self.__label_to_id[label]), label)
        self.updated = True

    def clearValues(self):
        if self.isEmpty():
            return
        self._values = [self.EMPTY_SELECTABLE_ITEM]
        self.updated = True

    @property
    def legal(self):
        return self._legal
    @legal.setter
    def legal(self, value:bool):
        self._legal = value
        self.updated = True

    def isEmpty(self):
        return (self._values == [self.EMPTY_SELECTABLE_ITEM])

    def fillIfEmpty(self, id=None, label=None):
        if self.isEmpty():
            self.add(id=id, label=label)

    def bind_values(self, non_empty_only=False):
        res = [item.id for item in self._values]
        if non_empty_only and self.EMPTY_FIELD_VID in res:
            res.remove(self.EMPTY_FIELD_VID)
        return res

    def labels(self):
        return [item.label for item in self._values]

    def __str__(self):
            return self._values

    def toJson(self):
        return {"field_id":self.id, "bind_value_ids":self.bind_values()}

    def get_field_struct(self):
        return self.__field_struct

class Field_sb(Field_msb):
    def __init__(self, id, slug, field_struct, values=None, fieldType=Field_type.SB):
        super().__init__(id, slug, field_struct, values, fieldType)

    def set(self, id=None, label=None):
        self.clearValues()
        self.add(id, label)

    def value_id(self):
        return self._values[0].id

    def value_label(self):
        return self._values[0].label

class Field_users(Field_msb):
    GENERIC_USER_LABEL = "generic_user_label"
    def __init__(self, id, slug, field_struct, values=[], fieldType=Field_type.USERS):
        super().__init__(id, slug, field_struct, values, fieldType=fieldType)

    def add(self, id):
        if not id:
            return
        new_label = self.GENERIC_USER_LABEL
        if (id in self._id_to_label.keys()):
            new_label = self._id_to_label[id]

        new_user = Field_msb.Selectable_item(id=id, label=new_label)

        self.add_selectable_item(new_user)

    def add_list(self, id_list):
        if id_list:
            for id in id_list:
                self.add(id=id)

    def remove(self, id):
        if id:
            for curUser in self._values():
                if id == curUser.id:
                    self._values.remove(curUser)
        self.updated = True

    def fillIfEmpty(self, id):
        if self.isEmpty():
            self.add(id=id)

    def get_user_reference(self, id):
        for item in self.get_field_struct()['values']:
            if item["id"] == id:
                return item["user_reference"]
        return None

class Field_user(Field_users):
    def __init__(self, id, slug, field_struct, values=None, fieldType=Field_type.USER):
        super().__init__(id, slug, field_struct, values, fieldType=fieldType)

    def set(self, id):
        self.clearValues()
        self.add(id)

    def value_id(self):
        return self._values[0].id

    def value_label(self):
        return self._values[0].label

    def get_user_reference(self, id=None):
        if not id and (len(self._values) > 0):
            id = self._values[0].id
        return super().get_user_reference(id)

    def get_user_real_name(self, id=None):
        user_ref = self.get_user_reference(id)
        if user_ref:
            return user_ref['real_name']
        return 'unknown_user'

class Field_float(Field):
    def __init__(self, id=None, slug=None, value=None):
        """
            Initialize a new instance of the class.

            Parameters:
            id (int): A positive integer representing the identifier. Default is None.
            slug (str): A string representing the slug. Default is None.
            value (float): A float representing the value. Default is None.
        """
        super().__init__(id, slug, Field_type.FLOAT)
        self.__value = value

    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value:float):
        self.updated = True
        self.__value = value

    def toJson(self):
        return {"field_id":self.id,"value":self.value}

class Field_date(Field):
    def __init__(self, id=None, slug=None, value=None):
        """
            Initialize a new instance of the class.

            Parameters:
            id (int): A positive integer representing the identifier. Default is None.
            slug (str): A string representing the slug. Default is None.
            value (datetime): A datetime representing the value. Default is None.
        """

        super().__init__(id, slug, Field_type.DATE)
        parsed_datetime = iso_to_datetime(value)
        self.__value = parsed_datetime
        self.__fieldType = Field_type.DATE

    @property
    def value(self) -> datetime:
        return self.__value
    @value.setter
    def value(self, value:datetime):
        self.updated = True
        self.__value = value

    def set_now(self):
        self.value = datetime.now()

    def __str__(self):
            return "{}-date: {}".format(self.slug, self.value)

    def toJson(self):
        return {"field_id":self.id,"value":datetime_to_iso(self.value)}

def get_empty_field(field_type:Field_type=None, field_id=None, field_slug=None, field_struct=None) -> Field:
    if field_struct:
        field_id = field_struct["field_id"]
        field_type = field_struct["type"]
        field_slug = field_struct["name"]
        if field_type in (Field_type.MSB, Field_type.SB):
            if (((not field_struct["values"]==[]) and ("username" in field_struct["values"][0])) or
                field_struct["values"]==[]):
                if field_type == Field_type.MSB:
                    field_type = Field_type.USERS
                elif field_type == Field_type.SB:
                    field_type = Field_type.USER

    if field_type == Field_type.NONE:
        return Field(id=field_id, slug=field_slug)
    elif field_type == Field_type.STRING:
        return Field_string(id=field_id, slug=field_slug)
    elif field_type == Field_type.TEXT:
        return Field_text(id=field_id, slug=field_slug)
    elif field_type == Field_type.BUTTONS:
        return Field_buttons(id=field_id, slug=field_slug)
    elif field_type == Field_type.ARTLINKS:
        return Field_artLinks(id=field_id, slug=field_slug)
    elif field_type == Field_type.FILES:
        return Field_files(id=field_id, slug=field_slug)
    elif field_type in (Field_type.MSB, Field_type.CB):
        return Field_msb(id=field_id, slug=field_slug, field_struct=field_struct, fieldType=field_type)
    elif field_type in (Field_type.SB, Field_type.RB):
        return Field_sb(id=field_id, slug=field_slug, field_struct=field_struct, fieldType=field_type)
    elif field_type in (Field_type.DATE, Field_type.SUBON, Field_type.LUD):
        return Field_date(id=field_id, slug=field_slug)
    elif field_type == Field_type.FLOAT:
        return Field_float(id=field_id, slug=field_slug)
    elif field_type in (Field_type.USER, Field_type.SUBBY, Field_type.LUBY):
        return Field_user(id=field_id, slug=field_slug, field_struct=field_struct, fieldType=field_type)
    elif field_type == Field_type.USERS:
        return Field_users(id=field_id, slug=field_slug, field_struct=field_struct)