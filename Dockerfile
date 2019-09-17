ARG BASE_IMAGE="alpine"

FROM $BASE_IMAGE

LABEL maintainer "Viktor Adam <rycus86@gmail.com>"

RUN apk --no-cache add python3 py3-pip git

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

RUN adduser -S webapp
USER webapp

ADD . /app
WORKDIR /app

ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python3", "server.py"]

# add app info as environment variables
ARG GIT_COMMIT
ENV GIT_COMMIT $GIT_COMMIT
ARG BUILD_TIMESTAMP
ENV BUILD_TIMESTAMP $BUILD_TIMESTAMP
