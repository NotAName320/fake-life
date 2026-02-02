from os import getenv

from dotenv import load_dotenv


def getenv_or_exit(env_var: str) -> str:
    retval = getenv(env_var)
    if retval:
        return retval
    raise ValueError(f"Could not find environment variable {env_var}")


load_dotenv()
BOT_OPERATOR_ROLE_NAME = getenv_or_exit("BOT_OPERATOR_ROLE_NAME")
CHARACTER_APPROVALS_CHANNEL_ID = int(getenv_or_exit("CHARACTER_APPROVALS_CHANNEL_ID"))
DISCORD_BOT_TOKEN = getenv_or_exit("DISCORD_BOT_TOKEN")
HOME_GUILD_ID = int(getenv_or_exit("HOME_GUILD_ID"))
MEMBER_ROLE_NAME = getenv_or_exit("MEMBER_ROLE_NAME")
MONGODB_CONNECTION_STRING = getenv_or_exit("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = getenv_or_exit("MONGODB_DATABASE_NAME")
