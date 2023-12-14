from dotenv import load_dotenv
from griptape.structures import Agent, Structure

load_dotenv()


def init_structure(*args, **init_params) -> Structure:
    return Agent()
