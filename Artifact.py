from tuleap_wrapper.Fields import *
from tuleap_wrapper import tracker_struct_manager as tsm
from tuleap_wrapper import tuleap_endpoint as tue
from typing import Self
import copy

class Artifact:
    __tracker_struct_manager = tsm.Tracker_struct_manager()
    __tuleap_endpoint = tue.TuleapEndpoint()

    def __init__(self, id=None, id_tracker=None, tracker_struct=None, raw_fields=None):
        self.__id = id
        self.__id_tracker = id_tracker
        self.__tracker_struct: tsm.TrackerStruct = tracker_struct
        self.__raw_fields = raw_fields
        # TODO: Require id_tracker in some way

        if not raw_fields:
            self.__raw_fields = dict()

        if (id_tracker):
            self.__tracker_struct = tsm.TrackerStruct(self.__tracker_struct_manager.get_ts(id_tracker))

        if (self.__tracker_struct):
            dependent_fields = self.__tracker_struct.ruleSet.get_dependent_field_ids()
            for fieldSlug, field in self.__raw_fields.items():
                if isinstance(field, Field) and field.id in dependent_fields:
                    field.dependent = True

    @classmethod
    def from_json(cls, jsonData, currentORprevious=None, tracker_struct_json=None) -> Self:
        if (currentORprevious):
            newJson = jsonData[currentORprevious]
            newJson["tracker"] = {}
            newJson["tracker"]["id"] = jsonData["tracker"]["id"]
            # tracker_struct_json = jsonData["tracker"]
            # Artifact.__tracker_struct_manager.set_ts(tracker_struct_json)
            tracker_struct_json = None # TODO:FIXME


            newJson["id"] = jsonData["id"] # Faut il bien changer l'id ?
        else:
            newJson = jsonData

        if not (tracker_struct_json):
            tracker_struct_json = Artifact.__tracker_struct_manager.get_ts(newJson["tracker"]["id"])

        curTrackerStruct = tsm.TrackerStruct(tracker_struct_json)

        fieldsDict = {}
        importedCounter = 0
        for value in newJson["values"]:
            field_id = value['field_id']
            if curTrackerStruct.field_exists(field_id):
                importedCounter = importedCounter + 1
                name = curTrackerStruct.idToName(field_id)
                fieldType = value['type']

                if (fieldType == Field_type.STRING):
                    fieldsDict[name] = Field_string(field_id, name,value['value'])

                elif (fieldType == Field_type.TEXT):
                    fieldsDict[name] = Field_text(field_id, name, value['value'], t_format=value['format'])

                elif(fieldType == Field_type.ARTLINKS):
                    myArtLinks_list=[]

                    for ilinks in value['links']:
                        myArtLinks_list.append(Field_artLinks.ArtLink(id_artifact=ilinks['id'],
                                                                    id_tracker=ilinks['tracker']['id'],
                                                                    direction = Field_artLinks.ArtLink.Direction.FORWARD,
                                                                    relation=ilinks['type']))
                    for ilinks in value['reverse_links']:
                        myArtLinks_list.append(Field_artLinks.ArtLink(id_artifact=ilinks['id'],
                                                                    id_tracker=ilinks['tracker']['id'],
                                                                    direction = Field_artLinks.ArtLink.Direction.REVERSE,
                                                                    relation=ilinks['type']))

                    fieldsDict[name] = Field_artLinks(field_id,name,myArtLinks_list)

                elif (fieldType in (Field_type.DATE, Field_type.SUBON, Field_type.LUD)):
                    if value['value']:
                        fieldsDict[name] = Field_date(field_id, name, value['value'])
                    else:
                        fieldsDict[name] = Field_date(field_id,name)

                elif (fieldType in (Field_type.MSB, Field_type.CB)):
                    isUserField = (not value["values"]==[]) and ("username" in value["values"][0])
                    if (isUserField):
                        fieldsDict[name] = Field_users(field_id, name, curTrackerStruct.get_field_info(field_id), value['values'])
                    else:
                        fieldsDict[name] = Field_msb(field_id, name, curTrackerStruct.get_field_info(field_id), value['values'], fieldType=fieldType)

                elif (fieldType in (Field_type.SB, Field_type.RB)):
                    isUserField = (not value["values"]==[]) and ("username" in value["values"][0])
                    if (isUserField):
                        fieldsDict[name] = Field_user(field_id, name, curTrackerStruct.get_field_info(field_id), value['values'])
                    else:
                        fieldsDict[name] = Field_sb(field_id, name, curTrackerStruct.get_field_info(field_id), value['values'], fieldType=fieldType)

                elif (fieldType in (Field_type.SUBBY, Field_type.LUBY)):
                    fieldsDict[name] = Field_user(field_id, name, curTrackerStruct.get_field_info(field_id), [value['value']], fieldType=fieldType)

                elif (fieldType == Field_type.FILES):
                    fieldsDict[name] = Field_files(field_id, name, value["file_descriptions"])

                elif (fieldType == Field_type.FLOAT):
                    fieldsDict[name] = Field_float(field_id, name, value["value"])
                else:
                    fieldsDict[name] = value

        print("ASARTIFACTS: Successfully imported " + str(importedCounter) + " fields into artifact " + str(newJson["id"]))
        return cls(id=newJson["id"],
                   id_tracker=newJson["tracker"]["id"],
                   tracker_struct=curTrackerStruct,
                   raw_fields=fieldsDict)

    @classmethod
    def from_id(cls, id) -> Self:
        json_art = cls.__tuleap_endpoint.get_artifact_by_id(id)
        return cls.from_json(json_art)

    @property
    def id(self):
        return self.__id
    @id.setter
    def id(self, value:int):
        self.__id = value

    @property
    def id_tracker(self):
        return self.__id_tracker
    @id_tracker.setter
    def id_tracker(self, value:int):
        self.__id_tracker = value

    @property
    def tracker_struct(self) -> tsm.TrackerStruct:
        return self.__tracker_struct

    def add_field(self, field:Field):
        self.__raw_fields[field.slug] = field

    def convert_msb(self, other_msb:Field_msb):
        new_msb = Field_msb(self.tracker_struct.nameToId(other_msb.slug),
                            other_msb.slug,
                            self.tracker_struct.get_field_info(other_msb.slug))
        new_msb.add_list(label_list=other_msb.labels())

        return new_msb

    def convert_sb(self, other_sb:Field_sb):
        new_sb = Field_sb(self.tracker_struct.nameToId(other_sb.slug),
                          other_sb.slug,
                          self.tracker_struct.get_field_info(other_sb.slug))
        new_sb.add_list(label_list=other_sb.labels())

        return new_sb

    def convert_links(self, other_artLinks:Field_artLinks):
        new_artLinks = Field_artLinks(id=self.tracker_struct.nameToId(other_artLinks.slug), slug=other_artLinks.slug)
        for link in other_artLinks.artLinks:
            new_artLinks.add_link(link)

        return new_artLinks

    def add_field_from_other_art(self, other_field:Field):
        new_field = copy.copy(other_field)
        new_field.id = self.tracker_struct.nameToId(other_field.slug)

        # Specific multilayer fields handling
        if (other_field.fieldType == Field_type.MSB):
            new_field = self.convert_msb(other_field)
        elif (other_field.fieldType == Field_type.SB):
            new_field = self.convert_sb(other_field)
        elif (other_field.fieldType == Field_type.ARTLINKS):
            new_field = self.convert_links(other_field)

        new_field.updated = True

        self.add_field(new_field)

    def get_field(self, fieldSlug, field_id=None) -> Field:
        if field_id:
            return self.get_field(self.tracker_struct.idToName(field_id))
        if not fieldSlug in self.__raw_fields.keys():
            self.init_field(fieldSlug)
            print("Requested field " + fieldSlug + " not found, initiating")

        return self.__raw_fields[fieldSlug]

    def get_fields(self):
        return self.__raw_fields

    def get_avail_fields(self):
        return self.__raw_fields.keys()

    def is_field(self, fieldSlug) -> bool:
        return fieldSlug in self.__raw_fields.keys()

    def init_field(self, fieldSlug):
        if self.is_field(fieldSlug):
            return
        elif not self.__tracker_struct.field_exists(fieldSlug):
            raise ValueError("ARTIFACT: 'init_field' requested slug not in tracker struct - " + fieldSlug)

        newField = get_empty_field(field_struct=self.__tracker_struct.get_field_info(fieldSlug))
        self.add_field(newField)

    def check_dependencies(self):
        invalid_tgt_fids = []
        invalid_src_fids = []

        for fid in self.__tracker_struct.ruleSet.get_dependent_field_ids(target_only=True):
            current_valid = True
            tgt_field:Field_msb = self.get_field("", fid)
            for tgt_vid in tgt_field.bind_values():
                valid_options = self.__tracker_struct.ruleSet.get_source_rules(tgt_field.id, tgt_vid)
                for (source_fid, source_vids) in valid_options.items():
                    source_msb:Field_msb = self.get_field("", source_fid)
                    if not any(value in source_vids for value in source_msb.bind_values()):
                        invalid_src_fids.append(source_fid)
                        current_valid = False

            if not current_valid:
                invalid_tgt_fids.append(fid)

        for fid in self.__tracker_struct.ruleSet.get_dependent_field_ids(source_only=True):
            current_valid = True
            src_field:Field_msb = self.get_field("", fid)
            for src_vid in src_field.bind_values():
                valid_options = self.__tracker_struct.ruleSet.get_target_rules(src_field.id, src_vid)
                for (target_fid, target_vids) in valid_options.items():
                    target_msb:Field_msb = self.get_field("", target_fid)
                    if not any(value in target_vids for value in target_msb.bind_values()):
                        invalid_tgt_fids.append(target_fid)
                        current_valid = False

            if not current_valid:
                invalid_src_fids.append(fid)

        return list(set(invalid_tgt_fids))

    def autocomplete_field(self, tgt_field:Field_msb, prefer_not_empty=False):
        tgt_options:list[tsm.Rule] = []
        source_rules = self.tracker_struct.ruleSet.get_source_rules(in_target_field_id=tgt_field.id)
        source_fids = source_rules.keys()
        for fid in source_fids:
            curField:Field_msb = self.get_field("", fid)
            for vid in curField.bind_values():
                if vid in source_rules[fid]:
                    tgt_options += self.tracker_struct.ruleSet.target_options(fid, vid, tgt_fid=tgt_field.id)

        options_to_remove:list[tsm.Rule] = []
        # Autocomplete to only not empty option
        if (prefer_not_empty and len(tgt_options) == 2):
            for opt in tgt_options:
                if opt.target_value_id == Field_msb.EMPTY_FIELD_VID:
                    options_to_remove.append(opt)

        # Autocomplete to EMPTY if allowed and many fields available
        if len(tgt_options) > 2:
            if any([opt.target_value_id == Field_msb.EMPTY_FIELD_VID for opt in tgt_options]):
                for opt in tgt_options:
                    if not (opt.target_value_id == Field_msb.EMPTY_FIELD_VID):
                        options_to_remove.append(opt)

        for opt in options_to_remove:
            tgt_options.remove(opt)

        if len(tgt_options) == 1:
            tgt_field.clearValues()
            tgt_field.add(id=tgt_options[0].target_value_id)
            print(f"ART {self.id}: Field {tgt_field.slug} autocompleted to {tgt_field.bind_values()}")
            return True
        return False

    def autocomplete_fields(self):
        max_iterations = 10
        invalid_fields = self.check_dependencies()

        count = 0
        while (count < max_iterations and len(invalid_fields) > 0):
            for field_id in invalid_fields:
                self.autocomplete_field(self.get_field("", field_id=field_id))
            invalid_fields = self.check_dependencies()

    def list_update(self, only_updated=False):
        updated_fields=[]

        for slug, field in self.__raw_fields.items():
            if isinstance(field, Field):
                if field.updated:
                    updated_fields.append(field.toJson())
                elif not only_updated and field.dependent:
                    updated_fields.append(field.toJson())
        return updated_fields

    def push_update(self, dependency_check=True, only_updated=False):
        # Check dependencies first:
        if dependency_check:
            invalid_fids = self.check_dependencies()
            remaining_invalid_fids = copy.copy(invalid_fids)
            if invalid_fids:
                print(f"ART {self.id}:  Invalid field dependencies found: {[self.tracker_struct.idToName(id) for id in invalid_fids]} ")
                for fid in invalid_fids:
                    if self.autocomplete_field(self.get_field("", field_id=fid)):
                        remaining_invalid_fids.remove(fid)
                if remaining_invalid_fids:
                    print(f"ART {self.id}: Cannot push update, remaining invalid fields {[self.tracker_struct.idToName(id) for id in remaining_invalid_fids]}")
                    return False

        updated_fields = self.list_update(only_updated=only_updated)
        if len(updated_fields) > 0:
            return Artifact.__tuleap_endpoint.update_artifact_by_id(self.id, updated_fields)
        else:
            print("ASARTIFACTS: Nothing to update")
            return False

    def upload(self):
        return Artifact.__tuleap_endpoint.create_artifact(self.id_tracker, values=self.list_update())
