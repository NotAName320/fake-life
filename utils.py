from os import getenv


def getenv_or_exit(env_var: str) -> str:
    retval = getenv(env_var)
    if retval:
        return retval
    raise ValueError(f"Could not find environment variable {env_var}")