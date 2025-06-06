import logging
import re

from prowjobsscraper import cir_metadata, equinix_usages, event, prowjob, step

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(
        self,
        event_store: event.EventStoreElastic,
        step_extractor: step.StepExtractor,
        cir_metadata_extractor: cir_metadata.CIResourceMetadataExtractor,
        equinix_usages_extractor: equinix_usages.EquinixUsagesExtractor,
    ):
        self._event_store = event_store
        self._step_extractor = step_extractor
        self._cir_metadata_extractor = cir_metadata_extractor
        self._equinix_usages_extractor = equinix_usages_extractor

    def execute(self, jobs: prowjob.ProwJobs):
        logger.info("%s jobs will be processed", len(jobs.items))

        # filter out non-assisted jobs
        jobs.items = [j for j in jobs.items if self._is_assisted_job(j)]

        # filter out jobs already stored
        known_jobs_build_ids = self._event_store.scan_build_ids()
        jobs.items = [
            j for j in jobs.items if j.status.build_id not in known_jobs_build_ids
        ]

        # Set CI resource metadata for each job
        self._cir_metadata_extractor.hydrate(jobs)

        # Retrieve executed steps for each job
        steps = self._step_extractor.parse_prow_jobs(jobs)

        # Retrieve equinix machines usages not already stored
        known_usages_identifiers = self._event_store.scan_usages_identifiers()
        unfiltered_usages = self._equinix_usages_extractor.get_project_usages()
        usages = [
            usage
            for usage in unfiltered_usages
            if self._should_index_usage(usage, known_usages_identifiers)
        ]

        # Store jobs and steps into their respective indices
        logger.info("%s jobs will be pushed to ES", len(jobs.items))
        self._event_store.index_prow_jobs(jobs.items)

        logger.info("%s steps will be pushed to ES", len(steps))
        self._event_store.index_job_steps(steps)

        logger.info("%s equinix usages will be pushed to ES", len(usages))
        self._event_store.index_equinix_usages(usages)

    def _should_index_usage(
        self,
        usage: equinix_usages.EquinixUsage,
        known_usages_identifiers: set[equinix_usages.EquinixUsageIdentifier],
    ) -> bool:
        return usage.to_identifier() not in known_usages_identifiers

    @staticmethod
    def _is_assisted_job(j: prowjob.ProwJob) -> bool:
        if j.spec.hidden:
            return False
        if j.status.state not in ("success", "failure"):
            return False
        elif not re.search("openshift.*assisted", j.spec.job):
            return False
        elif "openshift-release-fast-forward" in j.spec.job:
            # exclude fast-forward jobs
            return False
        elif j.status.description and "Overridden" in j.status.description:
            # exclude overridden builds
            # the url points to github instead of prow
            return False

        return True
