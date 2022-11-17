FROM registry.access.redhat.com/ubi8/python-39:latest

COPY --chown=1001:0 . .

RUN pip install --upgrade pip && make install

ENTRYPOINT [ "prow-jobs-scraper" ]
