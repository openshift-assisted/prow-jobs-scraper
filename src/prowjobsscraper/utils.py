from typing import Optional

from google.cloud import storage  # type: ignore
from pydantic import HttpUrl


def get_gcs_bucket_and_base_path_from_job_url(
    url: Optional[HttpUrl],
) -> tuple[str, str]:
    if url is None or url.path is None:
        raise ValueError("url is not set")

    http_path = url.path.split("/")
    bucket_name = http_path[3]
    base_path = url.path.split("/")[4:]

    return bucket_name, "/".join(base_path)


def download_from_gcs_as_string(client: storage.Client, bucket: str, path: str) -> str:
    gcs_bucket = client.bucket(bucket)
    gcs_blob = gcs_bucket.blob(path)
    return gcs_blob.download_as_string()
