import logging
import sys

from google.cloud import storage  # type: ignore
from opensearchpy import OpenSearch

from prowjobsscraper import cir_metadata, config, event, prowjob, scraper, step


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=config.LOG_LEVEL)

    es_client = OpenSearch(
        config.ES_URL,
        http_auth=(config.ES_USER, config.ES_PASSWORD),
        verify_certs=False,
        ssl_show_warn=False,
    )
    event_store = event.EventStoreElastic(
        client=es_client,
        job_index_basename=config.ES_JOB_INDEX,
        step_index_basename=config.ES_STEP_INDEX,
    )

    gcloud_client = storage.Client.create_anonymous_client()
    step_extractor = step.StepExtractor(
        client=gcloud_client, gcs_bucket_name=config.GCS_BUCKET_NAME
    )

    cir_metadata_extractor = cir_metadata.CIResourceMetadataExtractor(
        client=gcloud_client,
        gcs_bucket_name=config.GCS_BUCKET_NAME,
    )

    jobs = prowjob.ProwJobs.create_from_url(config.JOB_LIST_URL)
    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        cir_metadata_extractor,
    )
    scrape.execute(jobs)


if __name__ == "__main__":
    main()
