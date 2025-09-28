import os
import requests
from urllib.parse import urljoin
from tusclient import client
from tusclient.uploader.uploader import Uploader

CHUNK_SIZE = 2621440

class DocumentInterface:
    __server_base_url = None
    __server_auth_token = None

    def __init__(self, base_url:str, auth_token:str):
        self.__server_base_url = base_url
        self.__server_auth_token = auth_token
        self.__req_headers = {
            "Content-Type": "application/json",
            "X-Auth-AccessKey": self.__server_auth_token
        }

    def get_upload_json(self, file_path, folder_id, distant_filename=None):
        file_size = os.path.getsize(file_path)
        base_name = os.path.basename(file_path)
        if not distant_filename:
            distant_filename = base_name

        req_payload = {
            "file_properties": {
                "file_name": base_name,
                "file_size": file_size
            },
            "title": distant_filename
        }

        req_url = urljoin(self.__server_base_url, "/api/docman_folders/") + str(folder_id) + "/files"
        try:
            resp = requests.post(req_url, json=req_payload, headers=self.__req_headers, verify=False)
            resp.raise_for_status()
        except Exception as e:
            print(f"An error occurred: {e}")

        return resp.json()

    def get_new_upload_json(self, file_path, file_id=None):
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        req_payload = {
            "file_properties": {
                "file_name": file_name,
                "file_size": file_size,
                "mime_type": "application/octet-stream"  # Adjust as needed
            },
            "title": file_name,
            "description": "New revision uploaded via API.",
            "should_lock_file": False
        }

        req_url = urljoin(self.__server_base_url, "/api/docman_files/") + str(file_id) + "/versions"

        try:
            resp = requests.post(req_url, json=req_payload, headers=self.__req_headers, verify=False)
            resp.raise_for_status()
        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Response: {resp.text}")
            raise

        return resp.json()

    def push_upload(self, up_href:str, file_path:str):
        base_name = os.path.basename(file_path)
        upload_url = urljoin(self.__server_base_url, up_href)
        up_headers = {
            "Content-Type": "application/offset+octet-stream",
            "Tus-Resumable": "1.0.0",
            "X-Auth-AccessKey": self.__server_auth_token
        }
        tus_client = client.TusClient(upload_url, headers=up_headers)

        with open(file_path, 'rb') as f:
            uploader = Uploader(client=tus_client, file_stream=f, url=upload_url,
                                chunk_size=CHUNK_SIZE, metadata={"filename": base_name}, verify_tls_cert=False)
            uploader.upload()

    def update_file(self, file_path, file_id):
        up_json = self.get_new_upload_json(file_path, file_id)
        self.push_upload(up_json['upload_href'], file_path)

    def upload_file(self, file_path, folder_id, distant_filename=None):
        up_json = self.get_upload_json(file_path, folder_id, distant_filename)
        self.push_upload(up_json['file_properties']['upload_href'], file_path)

        return up_json["id"]



