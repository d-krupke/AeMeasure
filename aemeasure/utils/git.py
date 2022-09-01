import subprocess

__cached = None


def get_git_revision():
    global __cached
    if __cached != None:
        return __cached
    try:
        label = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("ascii")
        )
    except subprocess.CalledProcessError:
        print("Warning: Could not read git-revision!")
        label = None
    __cached = label
    return label
