import os
import sys
import tempfile
import subprocess

from docker_helper import read_configuration


def git_clone(owner, name):
    remote_url = 'https://github.com/%s/%s.git' % (owner, name)

    checkout_directory = tempfile.mkdtemp(prefix='%s_%s_' % (owner, name))

    try:
        subprocess.check_call(['git', 'clone', remote_url, checkout_directory])
        return checkout_directory
    except subprocess.CalledProcessError as ex:
        print('Failed to clone', '%s/%s' % (owner, name), ':', ex, file=sys.stderr)


def git_checkout(working_directory, branch_name):
    try:
        subprocess.call(['git', 'checkout', '-b', branch_name], cwd=working_directory)
        return True
    except subprocess.CalledProcessError as ex:
        print('Failed to switch to', branch_name, 'in', working_directory, ':', ex, file=sys.stderr)


def git_commit(working_directory, message):
    try:
        user_email = read_configuration('GIT_USER_EMAIL', '/var/secrets/autobump', None)
        if not user_email:
            return
        subprocess.call(['git', 'config', 'user.email', user_email], cwd=working_directory)

        user_name = read_configuration('GIT_USER_NAME', '/var/secrets/autobump', None)
        if not user_name:
            return
        subprocess.call(['git', 'config', 'user.name', user_name], cwd=working_directory)

        subprocess.call(['git', 'add', '.'], cwd=working_directory)
        subprocess.call(['git', 'commit', '-m',
                         '%s\n\nVersion bumped using https://github.com/rycus86/autobump' % message],
                        cwd=working_directory)

        return True
    except subprocess.CalledProcessError as ex:
        print('Failed to commit the change in', working_directory, ':', ex, file=sys.stderr)


def git_push(working_directory, owner, branch_name):
    try:
        subprocess.call(['git', 'config', 'credential.https://github.com.username', owner], cwd=working_directory)

        push_env = os.environ.copy()
        push_env['GIT_ASKPASS'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../util/git_askpass.sh'))
        push_env['GIT_PASSWORD'] = read_configuration('GIT_USER_PASSWORD', '/var/secrets/autobump', None)

        subprocess.call(['git', 'push', '-u', 'origin', branch_name],
                        cwd=working_directory,
                        env=push_env)

        return True
    except subprocess.CalledProcessError as ex:
        print('Failed to push to origin /', branch_name, 'from', working_directory, ':', ex, file=sys.stderr)


def git_diff(working_directory):
    try:
        return subprocess.check_output(['git', 'diff'], cwd=working_directory).decode('utf-8')
    except subprocess.CalledProcessError as ex:
        print('Failed to run `git diff` in', working_directory, ':', ex, file=sys.stderr)


def git_current_commit(working_directory):
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=working_directory).decode('utf-8')
    except subprocess.CalledProcessError as ex:
        print('Failed to run `git rev-parse HEAD` in', working_directory, ':', ex, file=sys.stderr)
