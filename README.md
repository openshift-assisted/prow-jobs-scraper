# Prow jobs scraper

## About

This tool scrape prow jobs related to the assisted installer and feed them into elasticsearch for further analysis.

## Install

```
$ make install
```

It is recommended to run it in a `virtualenv`.

## Usage

Once installed, run:

```
$ prow-jobs-scraper
```

If you want to run it locally, you can use the docker compose configuration located in `hack/es` directory. The `.env` file contains the environment variable to configure `prow-jobs-scraper` with a local Elasticsearch.

See below for the supported environment variables.

## Environment variables

`prow-jobs-scraper` relies on environment variables for its configuration, here is the list of them:

| Variable          |  Description                                                      | Example |
| --- | --- | --- |
| ES_URL            | Elasticsearch server where the jobs will be sent                  | https://localhost:9200 |
| ES_USER           | Elasticsearch user used for the authentication                    | |
| ES_PASSWORD       | Elasticsearch password used for the authentication                | |
| ES_STEP_INDEX     | Prefix name for the index that will store the steps of each job   | steps |
| ES_JOB_INDEX      | Prefix name for the index that will store the jobs                | jobs |
| JOB_LIST_URL      | Job list URL                                                      | https://prow.ci.openshift.org/prowjobs.js?omit=annotations,labels,decoration_config,pod_spec |
| LOG_LEVEL         | Level of the logs, default: INFO                                  | WARN |

## Unit tests

```
$ make unit-tests
```

It will install `tox` using `pip` and run it.

