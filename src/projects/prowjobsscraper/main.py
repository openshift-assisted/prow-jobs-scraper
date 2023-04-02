import logging
import sys

from google.cloud import storage  # type: ignore
from opensearchpy import OpenSearch

from projects.config import ES_JOB_INDEX, ES_PASSWORD, ES_STEP_INDEX, ES_URL, ES_USER
from projects.prowjobsscraper import equinix, event, prowjob, scraper, step
from projects.prowjobsscraper.config import JOB_LIST_URL, LOG_LEVEL


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=LOG_LEVEL)

    es_client = OpenSearch(
        ES_URL,
        http_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False,
        ssl_show_warn=False,
    )
    event_store = event.EventStoreElastic(
        client=es_client,
        job_index_basename=ES_JOB_INDEX,
        step_index_basename=ES_STEP_INDEX,
    )

    gcloud_client = storage.Client.create_anonymous_client()
    step_extractor = step.StepExtractor(client=gcloud_client)
    equinix_extractor = equinix.EquinixExtractor(client=gcloud_client)

    jobs = prowjob.ProwJobs.create_from_url(JOB_LIST_URL)
    scrape = scraper.Scraper(event_store, step_extractor, equinix_extractor)
    scrape.execute(jobs)


if __name__ == "__main__":
    main()
