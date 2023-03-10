from .utils import get_env_var, load_env

load_env()

BROKER_URL = get_env_var("BROKER_URL")
# TODO BACKEND_BROKER_URL