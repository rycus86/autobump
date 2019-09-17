from functools import wraps
from flask import request, abort, Response
from docker_helper import read_configuration


def check_auth_header():
    auth_key = read_configuration('AUTH_TOKEN', '/var/secrets/autobump', None)
    if not auth_key:
        return

    if request.headers.get('Webhook-Auth-Token') != auth_key:
        return abort(Response('Missing or invalid Webhook-Auth-Token header\n', status=401))


def is_dry_run(key):
    if read_configuration('DRY_RUN', '/var/secrets/autobump', None):
        return True

    if read_configuration('DRY_RUN_%s' % key, '/var/secrets/autobump', None):
        return True


def generates_text_response(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        return Response('\n'.join(part for part in func(*args, **kwargs)), mimetype='text/plain')

    return decorated
