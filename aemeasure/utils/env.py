import pkg_resources

__cached = None

def get_environment():
    global __cached
    if __cached is None:
        __cached = [
        {"name": str(pkg.project_name), "path": str(pkg.location), "version": str(pkg.parsed_version) } for pkg in pkg_resources.working_set
    ]
    return __cached