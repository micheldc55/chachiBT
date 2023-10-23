import json
import os
import random
import string
from datetime import datetime

from src.messages.messages import MessageHistory, Message


def generate_date_key_combination(dir_path="data/conversations") -> str:
    """Generated a random file name with todays date and 5 extra characters.

    :return: A file path with a unique id that can be used as a file name.
    :rtype: str
    """
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    # Create a filename using the current date and random string
    filename = f"{dir_path}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{rand_str}.json"

    return filename


def load_conversation_ids(dir_path="data/conversations") -> list:
    """Loads all files from a directory

    :param dir_path: Base path where all files are located, defaults to "data/conversations"
    :type dir_path: str, optional
    :return: A list of json paths
    :rtype: list
    """
    return [file.split('.json')[0] for file in os.listdir(dir_path) if file.endswith('.json')]


def read_history_from_id(json_path: str) -> MessageHistory:
    """Creates a message history from a path that is used to read the saved history file.

    :param json_path: Path to the file in the format: "base_dir" + "id" + ".json". YOU NEED TO PASS THE FULL PATH.
    :type json_path: str
    :return: A MessageHistory object containing the read history.
    :rtype: MessageHistory
    """
    with open(json_path) as f:
        hist_dict = json.load(f)

    messages_list_final = []

    for dict_message in hist_dict:
        messages_list_final.append(Message(dict_message["role"], dict_message["content"]))
        
    history = MessageHistory()
    history.populate_from_list(messages_list_final)

    return history