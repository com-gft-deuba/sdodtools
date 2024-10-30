import types
import subprocess

class CliException(subprocess.CalledProcessError):

    def __init__(self, message, cmd, r=None, stdout='', stderr=''):

        subprocess.CalledProcessError.__init__(self, r, cmd, stdout, stderr)

        message += "\n"
        message += f"Exit status was ({r})\n"
        message += f"STDOUT was:\n"

        for line in stdout.split(b"\n"): message += f"    {line.decode()}\n"

        message += f"STDERR was:\n"

        for line in stderr.split(b"\n"): message += f"    {line.decode()}\n"

        self.message = message
        self.r = r
        self.stdout = stdout
        self.stderr = stderr
