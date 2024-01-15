from typing import Optional

import mmh3
from google.cloud import storage  # type: ignore
from pydantic import HttpUrl


def get_gcs_base_path_from_job_url(
    url: Optional[HttpUrl],
) -> str:
    if url is None or url.path is None:
        raise ValueError("url is not set")

    base_path = url.path.split("/")[4:]
    return "/".join(base_path)


def download_from_gcs_as_string(client: storage.Client, bucket: str, path: str) -> str:
    gcs_bucket = client.bucket(bucket)
    gcs_blob = gcs_bucket.blob(path)
    return gcs_blob.download_as_string()


def generate_hash_from_strings(*strings) -> str:
    joined_string = "".join(strings)
    hashed_string = str(mmh3.hash(joined_string))
    return hashed_string
