import os


def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"{var_name} not found in environment variables")
    return value
