ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Copy data for add-on
COPY test.sh /
RUN chmod a+x /test.sh

COPY test.py /
RUN chmod a+x /test.py

RUN apk add --no-cache python3-dev gcc musl-dev

RUN python3 -m pip install --upgrade pip
RUN pip install aiohttp aiodns

CMD [ "/start.sh" ]