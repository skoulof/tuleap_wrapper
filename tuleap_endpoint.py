# Tuleap Rest client
from Tuleap.RestClient import Connection as con_api
from Tuleap.RestClient import Artifacts as art_api
from Tuleap.RestClient import Trackers as trk_api
from Tuleap.RestClient import Users as usr_api
from Tuleap.RestClient import UserGroups as ugp_api
from Tuleap.RestClient.Commons import CertificateVerification, FieldValues, Order
import requests

class ErrorCodes:
    UNAUTHORIZED = 401
    NOT_FOUND = 404

class TuleapEndpoint:
    # Class attributes to hold the base_url and auth_token
    base_url = None
    auth_token = None
    connection = None
    artifacts = None
    trackers = None
    users = None
    user_groups = None

    @classmethod
    def configure(cls, base_url, auth_token, cert_verification=True):
        """Method to set the base_url and auth_token once and for all."""
        cls.base_url = base_url
        cls.auth_token = auth_token
        cls.connection = con_api.Connection()

        if(cert_verification):
            verification = CertificateVerification.Enabled
        else:
            verification = CertificateVerification.Disabled

        success = cls.connection.set_access_key(base_url, auth_token, certificate_verification=verification)
        if success:
            cls.artifacts = art_api.Artifacts(cls.connection)
            cls.trackers = trk_api.Tracker(cls.connection)
            cls.users = usr_api.Users(cls.connection)
            cls.user_groups = ugp_api.UserGroups(cls.connection)
        else:
            raise ConnectionRefusedError("TuleapEndpoint: Connection failed")

    @classmethod
    def logout(cls):
        cls.connection.logout()

    def __init__(self):
        """Initializer that ensures each instance has access to the configured variables."""
        if self.base_url is None or self.auth_token is None:
            raise ConnectionError("TuleapEndpoint not configured. Please call `configure` before creating instances.")

    def get_artifact_by_id(self, artifact_id):
        success = self.artifacts.request_artifact(artifact_id)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Get artifact {str(artifact_id)} request failed with status code {response.status_code}: {response.text}")
        return self.artifacts.get_data()

    def get_tracker_struct_by_id(self, tracker_id):
        success = self.trackers.request_tracker(tracker_id)
        if not success:
            response = self.trackers.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Get tracker struct {str(tracker_id)} request failed with status code {response.status_code}: {response.text}")
        return self.trackers.get_data()

    def update_artifact_by_id(self, artifact_id, values):
        success = self.artifacts.update_artifact(artifact_id, values)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Update artifact {str(artifact_id)} request failed with status code {response.status_code}: {response.text}")
        return success

    def create_artifact(self, tracker_id, values_by_field=None, values=None):
        success = self.artifacts.create_artifact(tracker_id, values_by_field, values)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Create artifact on tracker {str(tracker_id)} request failed with status code {response.status_code}: {response.text}")
        return success

    def get_user_by_id(self, user_id):
        success = self.users.request_user(user_id)
        if not success:
            response = self.users.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Get user {str(user_id)} request failed with status code {response.status_code}: {response.text}")
        return self.users.get_data()

    def get_user_group_by_id(self, group_id):
        success = self.user_groups.request_user_group(group_id)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Get user group {str(group_id)} request failed with status code {response.status_code}: {response.text}")
        return self.user_groups.get_data()

    def get_users_in_group(self, group_id):
        success = self.user_groups.request_users_in_group(group_id)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Get users in group {str(group_id)} request failed with status code {response.status_code}: {response.text}")
        return self.user_groups.get_data()

    def add_users_in_group(self, group_id, user_ids):
        success = self.user_groups.add_users_in_group(group_id, user_ids)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Add users in group {str(group_id)} request failed with status code {response.status_code}: {response.text}")
        return success

    def remove_users_in_group(self, group_id, user_ids):
        success = self.user_groups.remove_users_in_group(group_id, user_ids)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Remove users in group {str(group_id)} request failed with status code {response.status_code}: {response.text}")
        return success

    def set_users_in_group(self, group_id, user_ids):
        success = self.user_groups.set_user_group_users(group_id, user_ids)
        if not success:
            response = self.artifacts.get_last_response_message()
            raise requests.exceptions.HTTPError(f"Set users in group {str(group_id)} request failed with status code {response.status_code}: {response.text}")
        return success

    def get_artifact_id_list(self,
                             tracker_id,
                             limit=10,
                             offset=None,
                             query=None,
                             expert_query=None,
                             order=Order.Ascending):
        REQUEST_LIMIT = 150
        current_offset = 0
        if (limit):
            REQUEST_LIMIT = limit
        if (offset):
            current_offset = offset

        returned_count = REQUEST_LIMIT
        result = []
        while (returned_count==REQUEST_LIMIT):
            success = self.trackers.request_artifact_list(tracker_id=tracker_id,
                                            field_values=FieldValues.No,
                                            limit=REQUEST_LIMIT,
                                            offset=current_offset,
                                            query=query,
                                            expert_query=expert_query,
                                            order=order)
            if not success:
                self.unsuccessful_warning(self.trackers.get_last_response_message().status_code, "create_artifact, tracker_id=" + str(tracker_id))
                break
            local_result = self.trackers.get_data()
            returned_count = len(local_result)
            for item in local_result:
                result.append(item["id"])
            current_offset+=REQUEST_LIMIT

        return result

    def unsuccessful_warning(self, inErrorCode, inContext=None):
        print("TuleapEndpoint request failed: " + inContext + "\n")
        if inErrorCode == ErrorCodes.UNAUTHORIZED:
            raise ConnectionError(self.connection.get_last_response_message().content)
        else:
            print(self.connection.get_last_response_message().content)
