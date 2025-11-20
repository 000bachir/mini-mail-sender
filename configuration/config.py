"""
to load virtual environement variables
"""

import os
from dotenv import load_dotenv, dotenv_values, find_dotenv


def loading_env_variables(variable: str):
    # loading a variable from an env file
    try:
        # locate the env file
        env_path = find_dotenv()
        if not env_path:
            raise FileNotFoundError(
                "failed to locate the .env file from the root of the project "
            )
        # load_dotenv will output them in a dictionary format in the console
        load_dotenv(env_path)
        if not dotenv_values(env_path):
            raise ValueError(
                "the env file has no variable inside please check the file"
            )
        # get the values out of the file
        values = os.getenv(variable)
        if not values:
            raise KeyError(
                f"variable {variable} has not been found in the env file please check the spelling"
            )
        return values
    except Exception as e:
        print(
            f"failed to load the variables from the env file please check the console : {e}"
        )
