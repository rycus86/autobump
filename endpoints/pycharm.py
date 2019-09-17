from flask import request, abort, Response

from endpoints import generates_text_response, is_dry_run
from tasks.edit import contents_of
from tasks.git import git_clone, git_checkout, git_commit, git_diff, git_push, git_current_commit
from util.jetbrains import parse_jetbrains_product_version
from tasks import slack


@generates_text_response
def update_pycharm(owner, name):
    new_version, main_version, build_version = parse_jetbrains_product_version(request.json['Name'])

    yield 'Updating to PyCharm (%s) %s (%s / %s)\n' % (name, new_version, main_version, build_version)

    directory = git_clone(owner, name)
    if not directory:
        return abort(Response('Failed to clone the project from %s/%s' % (owner, name), status=500))

    if not git_checkout(directory, new_version):
        return abort(Response('Failed to checkout a new branch at %s' % new_version, status=500))

    with contents_of(directory, 'Dockerfile') as f:
        f.edit('ARG PYCHARM_VERSION=.+', 'ARG PYCHARM_VERSION=%s' % main_version)
        f.edit('ARG PYCHARM_BUILD=.+', 'ARG PYCHARM_BUILD=%s' % build_version)

    diff = git_diff(directory)
    if not diff:
        return abort(Response('Failed to list the changes in %s' % directory, status=500))

    if not git_commit(directory, 'Update to %s (%s)' % (main_version, build_version)):
        return abort(Response('Failed to commit changes in %s' % directory, status=500))

    yield 'Updated, difference:\n%s\n' % diff

    slack_message = '''
Update *PyCharm* (%s) to `%s` (`%s` / `%s`)
```
%s
```
    '''.strip() % (name, new_version, main_version, build_version, diff.strip())

    if not is_dry_run('PYCHARM'):
        if not git_push(directory, owner, new_version):
            return abort(Response('Failed to push the new branch from %s' % directory, status=500))

        head_commit = git_current_commit(directory)
        if head_commit:
            slack_message += '\nLink: https://github.com/%s/%s/commit/%s' % (owner, name, head_commit)

    slack.send_message(slack_message)
