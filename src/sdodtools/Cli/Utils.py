import subprocess

##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

##############################################################################
##############################################################################

class CliException(subprocess.CalledProcessError):

    @classmethod
    def from_result(cls, message=None, cmd=None, r=None, stdout=None, stderr=None, is_success=lambda r, stdout, stderr: r ==0):

        if is_success(r, stdout, stderr): return

        return cls(message, cmd, r, stdout, stderr)

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

    def __str__(self): return self.message
