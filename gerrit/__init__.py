import paramiko
import json
from subprocess import list2cmdline


class QueryOptions:

    Files = "--files"
    CurrentPatchSet = "--current-patch-set"
    Comments = "--comments"
    CommitMessage = "--commit-message"
    Dependencies = "--dependencies"
    AllApprovals = "--all-approvals"


class GerritError(RuntimeError):
    pass


class ResponseIter(object):
    def __init__(self, stdout, stderr):
        self._stdout = stdout
        self._stderr = stderr
        self._flag = False

    def __iter__(self):
        return self

    def next(self):
        for l in self._stdout:
            self._flag = True
            obj = json.loads(l)
            if "rowCount" in obj:
                continue
            if "type" in obj and obj['type'] == "error":
                raise GerritError(obj['message'])

            return obj

        if not self._flag:
            raise GerritError(self._stderr.read())

        self.close()
        raise StopIteration()

    def __next__(self):
        return self.next()

    def close(self):
        self._stdout.close()
        self._stderr.close()

    def __del__(self):
        self.close()


class Gerrit(object):
    def __init__(self, host, port, username, pkey):
        self._host = host
        self._port = int(port)
        self._username = username
        self._pkey = pkey

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self._host, port=self._port,
                       username=self._username, pkey=self._pkey)

        self._client = client

    def query(self, query, limit=None, options=[], resume_sortkey=None):
        cmd = ["gerrit", "query", "--format", "json"]
        for option in options:
            cmd.append(option)

        cmd.append(query)
        if limit is not None:
            cmd.append("limit:%d" % limit)

        if resume_sortkey is not None:
            cmd.append("resume_sortkey:%s" % resume_sortkey)

        cmdline = list2cmdline(cmd)

        stdin, stdout, stderr = self._client.exec_command(cmdline)
        stdin.close()
        return ResponseIter(stdout, stderr)

    def _run_cmd(self, cmd):
        cmdline = list2cmdline(cmd)

        stdin, stdout, stderr = self._client.exec_command(cmdline)
        stdin.close()
        out = stdout.read()
        stdout.close()
        err = stderr.read()
        stderr.close()

        if out != "":
            GerritError(out)

        if err != "":
            GerritError(err)

    def review(self, commit, project=None, message=None, label=None):
        cmd = ["gerrit", "review"]
        if project is not None:
            cmd.extend(("--project", project))

        if message is not None:
            cmd.extend(("--message", message))

        if label is not None:
            cmd.extend(("--label", "%s=%d" % label))

        cmd.append(commit)

        self._run_cmd(cmd)

    def set_reviewers(self, commit, add=[], remove=[]):
        cmd = ["gerrit", "set-reviewers"]
        for reviewer in add:
            cmd.extend(("--add", reviewer))

        for reviewer in remove:
            cmd.extend(("--remove", reviewer))

        cmd.append(commit)

        self._run_cmd(cmd)

    def close(self):
        self._client.close()
