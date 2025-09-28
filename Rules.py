from typing import Self

class Rule:
    def __init__(self, source_field_id, source_value_id, target_field_id, target_value_id):
        self.source_field_id = source_field_id
        self.source_value_id = source_value_id
        self.target_field_id = target_field_id
        self.target_value_id = target_value_id

    @classmethod
    def from_json(cls, jsonRule):
        return cls(jsonRule["source_field_id"], jsonRule["source_value_id"], jsonRule["target_field_id"], jsonRule["target_value_id"])

    def to_second_level(self) -> dict:
         return {self.target_field_id:[self.target_value_id]}

    def to_first_rule(self) -> dict:
         return {self.source_value_id: self.to_second_level()}

    def __str__(self):
         return str(self.source_field_id) + "/" + str(self.source_value_id) + "-->" + str(self.target_field_id) + "/" + str(self.target_value_id)

    def __repr__(self):
        return str(self)

    def __eq__(self, value:Self):
        return (self.source_field_id == value.source_field_id and
                self.source_value_id == value.source_value_id and
                self.target_field_id == value.target_field_id and
                self.target_value_id == value.target_value_id)

class RuleSet:
    def __init__(self, in_rules):
        self.__targets = dict()
        self.__sources = dict()
        self.__all_rules = [Rule.from_json(raw_rule) for raw_rule in in_rules]
        self.__dependent_field_ids = set()

        for rule in self.__all_rules:
            self.__dependent_field_ids.add(rule.source_field_id)
            self.__dependent_field_ids.add(rule.target_field_id)

    def add_rule(self, new_rule:Rule):
        if not new_rule in self.__all_rules:
            self.__all_rules.append(new_rule)
            self.__dependent_field_ids.add(new_rule.source_field_id)
            self.__dependent_field_ids.add(new_rule.target_field_id)

        if not new_rule.source_field_id in self.__targets.keys():
            self.__targets[new_rule.source_field_id] = new_rule.to_first_rule()
            return
        if not new_rule.source_value_id in self.__targets[new_rule.source_field_id].keys():
             self.__targets[new_rule.source_field_id][new_rule.source_value_id] = new_rule.to_second_level()
             return
        if not new_rule.target_field_id in self.__targets[new_rule.source_field_id][new_rule.source_value_id].keys():
             self.__targets[new_rule.source_field_id][new_rule.source_value_id][new_rule.target_field_id] = [new_rule.target_value_id]
             return
        if not new_rule.target_value_id in self.__targets[new_rule.source_field_id][new_rule.source_value_id][new_rule.target_field_id]:
            self.__targets[new_rule.source_field_id][new_rule.source_value_id][new_rule.target_field_id].append(new_rule.target_value_id)
        return

    def target_options(self, src_fid, src_vid, tgt_fid=None) -> list[Rule]:
        result = []
        for rule in self.__all_rules:
            if (rule.source_field_id == src_fid and
                rule.source_value_id == src_vid and
                (not tgt_fid or rule.target_field_id == tgt_fid)):
                result.append(rule)
        return result

    def is_valid(self, source_field_id, source_value_id, target_field_id, target_value_id):
        test_rule = Rule(source_field_id,
                         source_value_id,
                         target_field_id,
                         target_value_id)

        return test_rule in self.__all_rules

    def get_rule(self, index:int) -> Rule:
        if len(self.__all_rules) > index :
             return self.__all_rules[index]

    def get_all_rules(self):
         return self.__all_rules

    def get_dependent_field_ids(self, source_only=False, target_only=False):
        result = set()
        if source_only and not target_only:
            for rule in self.__all_rules:
                result.add(rule.source_field_id)
        elif target_only:
            for rule in self.__all_rules:
                result.add(rule.target_field_id)
        else:
            for rule in self.__all_rules:
                result.add(rule.source_field_id)
                result.add(rule.target_field_id)
        return result

    def get_source_rules(self, in_target_field_id, in_target_value_id=None) -> dict:
        result = dict()
        for rule in self.__all_rules:
            if (rule.target_field_id == in_target_field_id and
                (rule.target_value_id == in_target_value_id or not in_target_value_id)):
                if rule.source_field_id in result.keys():
                    result[rule.source_field_id].append(rule.source_value_id)
                else:
                    result[rule.source_field_id] = [rule.source_value_id]
        return result


    def get_target_rules(self, in_source_field_id, in_source_value_id):
        result = dict()
        for rule in self.__all_rules:
            if (rule.source_field_id == in_source_field_id and
                rule.source_value_id == in_source_value_id):
                if rule.target_field_id in result.keys():
                    result[rule.target_field_id].append(rule.target_value_id)
                else:
                    result[rule.target_field_id] = [rule.target_value_id]

        return result
