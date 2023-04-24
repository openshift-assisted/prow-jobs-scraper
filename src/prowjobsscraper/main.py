import logging
import sys
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from google.cloud import storage  # type: ignore
from opensearchpy import OpenSearch

from prowjobsscraper import (
    config,
    equinix_metadata,
    equinix_usages,
    event,
    prowjob,
    scraper,
    step,
)


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
        usage_index_basename=config.ES_USAGE_INDEX,
    )

    gcloud_client = storage.Client.create_anonymous_client()
    step_extractor = step.StepExtractor(client=gcloud_client)
    equinix_metadate_extractor = equinix_metadata.EquinixMetadataExtractor(
        client=gcloud_client
    )

    usages_scrape_end_time = datetime.now(tz=timezone.utc)
    if (
        config.EQUINIX_USAGES_SCRAPE_INTERVAL
        == equinix_usages.EquinixUsagesScrapeInterval.HOUR
    ):
        usages_scrape_start_time = usages_scrape_end_time - relativedelta(hours=1)
    elif (
        config.EQUINIX_USAGES_SCRAPE_INTERVAL
        == equinix_usages.EquinixUsagesScrapeInterval.DAY
    ):
        usages_scrape_start_time = usages_scrape_end_time - relativedelta(days=1)
    elif (
        config.EQUINIX_USAGES_SCRAPE_INTERVAL
        == equinix_usages.EquinixUsagesScrapeInterval.WEEK
    ):
        usages_scrape_start_time = usages_scrape_end_time - relativedelta(weeks=1)
    else:
        usages_scrape_start_time = usages_scrape_end_time - relativedelta(months=1)

    equinix_usages_extractor = equinix_usages.EquinixUsagesExtractor(
        project_id=config.EQUINIX_PROJECT_ID,
        project_token=config.EQUINIX_PROJECT_TOKEN,
        start_time=usages_scrape_start_time,
        end_time=usages_scrape_end_time,
    )

    jobs = prowjob.ProwJobs.create_from_url(config.JOB_LIST_URL)
    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadate_extractor,
        equinix_usages_extractor,
    )
    scrape.execute(jobs)


if __name__ == "__main__":
    main()
