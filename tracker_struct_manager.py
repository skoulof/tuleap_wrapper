import json
import os
import tuleap_wrapper.tuleap_endpoint as tue
from tuleap_wrapper.Rules import *

ts_suffix = "_ts.json"
ts_folder = "tracker_structs/"

class Tracker_struct_manager:
    __tracker_structs = {}
    __tuleap_endpoint = tue.TuleapEndpoint()
    def __init__(self):
        pass

    def set_ts(self, tracker_struct):
        ts_id = tracker_struct["id"]
        Tracker_struct_manager.__tracker_structs[ts_id] = tracker_struct
        if not os.path.exists(ts_folder):
            os.makedirs(ts_folder)
            print(f"TSM: Created folder {ts_folder}")
        with open(ts_folder + str(ts_id) + ts_suffix, 'w', encoding='utf-8') as file:
            json.dump(tracker_struct, file, indent=4)
        print("TSM: Saved tracker struct to disk " + str(ts_id))

    def get_ts(self, tracker_struct_id):
        if tracker_struct_id not in Tracker_struct_manager.__tracker_structs:
            ts_file_path = ts_folder + str(tracker_struct_id) + ts_suffix
            if (os.path.isfile(ts_file_path)):
                with open(ts_file_path, 'r', encoding='utf-8') as file:
                    Tracker_struct_manager.__tracker_structs[tracker_struct_id] = json.load(file)
                    print("TSM: Loaded tracker struct from disk " + str(tracker_struct_id))
            else:
                newTs = Tracker_struct_manager.__tuleap_endpoint.get_tracker_struct_by_id(tracker_struct_id)
                print("TSM: Fetched tracker struct with api: " + str(tracker_struct_id))
                self.set_ts(newTs)

        return Tracker_struct_manager.__tracker_structs[tracker_struct_id]

class TrackerStruct:
    def __init__(self, json_data):
        self.id_tracker = json_data["id"]
        self.fields = {field["name"]: field for field in json_data["fields"]}
        self.ruleSet = RuleSet(json_data["workflow"]["rules"]["lists"])

    def get_field_info(self, identifier):
        if isinstance(identifier, str):
            field_info = self.fields.get(identifier)
            if field_info is None:
                raise KeyError(f"Field with name '{identifier}' not found.")
            return field_info
        elif isinstance(identifier, int):
            for field_name, field_info in self.fields.items():
                if field_info["field_id"] == identifier:
                    return field_info
            raise KeyError(f"Field with ID '{identifier}' not found.")
        else:
            raise TypeError("Identifier must be a string (name) or an integer (field_id).")

    def field_exists(self, identifier):
        """Checks if a field exists, by name or ID."""
        try:
            self.get_field_info(identifier)
            return True
        except KeyError:
            return False

    def idToName(self, field_id):
        """Gets the name of a field given its ID."""
        for field_name, field_info in self.fields.items():
            if field_info["field_id"] == field_id:
                return field_name
        raise KeyError(f"Field with ID '{field_id}' not found.")

    def nameToId(self, field_name):
        """Gets the ID of a field given its name."""
        field_info = self.fields.get(field_name)
        if field_info is None:
            raise KeyError(f"Field with name '{field_name}' not found.")
        return field_info["field_id"]
