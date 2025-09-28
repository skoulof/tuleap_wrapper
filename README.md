# tuleap_wrapper

A comprehensive Python wrapper for the Tuleap REST API, providing high-level, object-oriented abstractions for interacting with Tuleap trackers, artifacts, users, and documents. This library simplifies common operations by encapsulating API calls into intuitive Python classes and methods.

## Features

*   **Object-Oriented Interface**: Modern, class-based interfaces for Tuleap entities like `Artifact`, `User`, and `UserGroup`.
*   **Advanced Field Management**: Strong-typed classes for various Tuleap field types (`string`, `text`, `date`, `select-box`, `multi-select-box`, `artifact-links`, `users`, etc.), simplifying data manipulation.
*   **Automatic Dependency Resolution**: Intelligently handles cascading field dependencies (rules), with capabilities for autocompletion and validation before updates.
*   **Tracker Structure Caching**: Automatically fetches and caches tracker structures locally to minimize API requests and improve performance.
*   **CRUD Operations**: Full support for creating, retrieving, and updating artifacts.
*   **Document Management**: Upload and update files to the Tuleap Document Manager (Docman) using the resumable TUS protocol.
*   **Centralized Configuration**: Configure your Tuleap instance URL and access key in one place.

## Installation

This library depends on `Tuleap.RestClient` and `tusclient`. You can install them using pip:

```shell
pip install Tuleap.RestClient tusclient requests
```

After installing the dependencies, clone this repository or copy the source files into your Python project.

## Getting Started

### 1. Configuration

Before using the wrapper, you must configure it with your Tuleap instance URL and a personal access key. This only needs to be done once per application session.

```python
from tuleap_wrapper.tuleap_endpoint import TuleapEndpoint

TULEAP_URL = "https://your-tuleap-instance.com"
ACCESS_KEY = "your-personal-access-key" # tlp-k-....

# Configure the connection (disable cert verification if using a self-signed certificate)
TuleapEndpoint.configure(TULEAP_URL, ACCESS_KEY, cert_verification=False)
```

### 2. Working with Artifacts

#### Retrieving an Artifact

Fetch an existing artifact by its ID. The wrapper automatically retrieves the tracker structure and parses all field values into corresponding objects.

```python
from tuleap_wrapper.Artifact import Artifact

# Get artifact with ID 123
my_artifact = Artifact.from_id(123)

print(f"Artifact ID: {my_artifact.id}")
print(f"Tracker ID: {my_artifact.id_tracker}")
```

#### Accessing and Modifying Fields

Access fields using their slug (name) and modify their values. The wrapper tracks which fields have been updated.

```python
# Get a string field
title_field = my_artifact.get_field("title")
print(f"Current title: {title_field.value}")

# Change the title
title_field.value = "A new title for the artifact"

# Get a single-select box (SB) field and change its value
status_field = my_artifact.get_field("status")
print(f"Current status: {status_field.value_label()}")
status_field.set(label="In Progress")

# Get a multi-select box (MSB) field and add a value
components_field = my_artifact.get_field("components")
components_field.add(label="Backend")

# Get an artifact links field and add a new link
links_field = my_artifact.get_field("links")
links_field.add_link(
    artifact_id=456,
    relation=links_field.ArtLink.Relation.RELATE_TO
)
```

#### Pushing Updates

Push all modified fields back to Tuleap. The `push_update` method can automatically check and resolve field dependencies before sending the request.

```python
# Push the changes to Tuleap
# If dependency_check is True (default), it will try to autocomplete dependent fields.
was_updated = my_artifact.push_update()

if was_updated:
    print(f"Artifact {my_artifact.id} was updated successfully.")
else:
    print(f"Failed to update artifact {my_artifact.id} or no changes to push.")
```

#### Creating a New Artifact

Create a new `Artifact` instance, set its fields, and upload it to a specific tracker.

```python
from tuleap_wrapper.Artifact import Artifact

# Create an artifact object for tracker with ID 78
new_artifact = Artifact(id_tracker=78)

# Initialize and set values for the fields
new_artifact.get_field("title").value = "New bug found in API"
new_artifact.get_field("description").value = "The /users endpoint returns a 500 error."
new_artifact.get_field("status").set(label="New")

# Upload the new artifact to Tuleap
new_artifact.upload()
print("New artifact created successfully!")
```

### 3. Uploading Documents

Use the `DocumentInterface` to upload files to the Tuleap Document Manager.

```python
from tuleap_wrapper.Documents import DocumentInterface

# The interface uses the configured URL and access key from TuleapEndpoint
doc_interface = DocumentInterface(TULEAP_URL, ACCESS_KEY)

# Upload a file to a specific folder (e.g., folder ID 99)
file_id = doc_interface.upload_file(
    file_path="/path/to/my-log-file.log",
    folder_id=99
)
print(f"File uploaded successfully with new document ID: {file_id}")
```

### 4. Extending the definition

Copy the structure of the Artifact class to make your own, reflecting your tracker structure:

```python
from tuleap_wrapper.Artifact import Artifact

class myArtifact(Artifact):
    class slugs:
        STRING_FIELD = "string_field_name"
        MSB_FIELD = "msb_field_name"
        
    @property
    def string_field(self):
        return self.get_field(self.slugs.STRING_FIELD)

    @property
    def msb_field(self):
        return self.get_field(self.slugs.MSB_FIELD)
```

## Core Components

*   `tuleap_endpoint.py`: The central connection client. Handles all raw communication with the Tuleap REST API and authentication.
*   `Artifact.py`: A high-level class representing a Tuleap artifact. It acts as a container for its fields and provides methods for retrieval, modification, and creation.
*   `Fields.py`: Contains a collection of classes, each representing a specific Tuleap field type (e.g., `Field_string`, `Field_msb`, `Field_artLinks`). These classes manage the field's data and formatting.
*   `tracker_struct_manager.py`: Responsible for fetching and caching tracker structures. This avoids redundant API calls and provides field and rule definitions to other modules.
*   `Rules.py`: Models the field dependency rules defined in a tracker's workflow. Used by the `Artifact` class to validate and autocomplete field values.
*   `Documents.py`: Provides an interface for interacting with the Tuleap Document Manager, primarily for file uploads.
*   `User.py` & `UserGroup.py`: Classes for retrieving information about Tuleap users and managing members of user groups.