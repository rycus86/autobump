import re
import requests
from flask import request, abort, Response

from endpoints import generates_text_response, is_dry_run
from tasks.edit import contents_of
from tasks.git import git_clone, git_checkout, git_commit, git_diff, git_push, git_current_commit
from util.jetbrains import parse_jetbrains_product_version
from tasks import slack


@generates_text_response
def update_goland(owner, name):
    new_version, display_version, main_version, build_version = parse_jetbrains_product_version(request.json['Name'])

    yield 'Updating to GoLand %s (%s / %s)\n' % (new_version, main_version, build_version)

    go_version = fetch_latest_go_version()
    if not go_version:
        return abort(Response('Failed to fetch the latest Go version', status=500))

    yield 'Will use Go version %s\n' % go_version

    directory = git_clone(owner, name)
    if not directory:
        return abort(Response('Failed to clone the project from %s/%s' % (owner, name), status=500))

    if not git_checkout(directory, new_version):
        return abort(Response('Failed to checkout a new branch at %s' % new_version, status=500))

    with contents_of(directory, 'Dockerfile') as f:
        f.edit('ARG GO_VERSION=.+', 'ARG GO_VERSION=%s' % go_version)
        f.edit('ARG GOLAND_VERSION=.+', 'ARG GOLAND_VERSION=%s' % main_version)
        f.edit('ARG GOLAND_BUILD=.+', 'ARG GOLAND_BUILD=%s' % build_version)

    diff = git_diff(directory)
    if not diff:
        return abort(Response('Failed to list the changes in %s' % directory, status=500))

    if not git_commit(directory, 'Update to %s (%s)' % (display_version, build_version)):
        return abort(Response('Failed to commit changes in %s' % directory, status=500))

    yield 'Updated, difference:\n%s\n' % diff

    slack_message = '''
Update *GoLand* to `%s` (`%s` / `%s`) on Go version `%s`
```
%s
```
    '''.strip() % (new_version, main_version, build_version, go_version, diff.strip())

    if not is_dry_run('GOLAND'):
        if not git_push(directory, owner, new_version):
            return abort(Response('Failed to push the new branch from %s' % directory, status=500))

        head_commit = git_current_commit(directory)
        if head_commit:
            slack_message += '\nLink: https://github.com/%s/%s/commit/%s' % (owner, name, head_commit)

    slack.send_message(slack_message)


def fetch_latest_go_version():
    response = requests.get('https://golang.org/dl/')
    if response.status_code == 200:
        for match in re.finditer(
                r'<a class="download downloadBox" href=".*/go([0-9.]+)\.linux-amd64\.tar\.gz">',
                response.text):
            return match.group(1)
