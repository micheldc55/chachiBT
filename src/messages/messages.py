import json
import random
import string
from datetime import datetime


class Message:
    """Create a message object for an LLM."""

    def __init__(self, role: str, message: str):
        if role not in ["system", "user", "assistant"]:
            raise ValueError("Message role must be either 'system', 'user' or 'assistant'.")
        self.message = message
        self.role = role

    def __repr__(self):
        message_text = self.message if len(self.message) < 20 else self.message[:18] + "..."
        return f"""Message(role={self.role}, message="{message_text}")"""


class MessageHistory:
    """Manages the history of a conversation between a bot and a user.

    Attributes:
        messages (list): A list of Message objects representing the conversation history.
    """

    def __init__(self, has_sys_msg: bool = True):
        self.messages = []
        self.has_sys_msg = has_sys_msg

    def add_message(self, message: Message):
        """Adds a new message to the conversation history.

        Args:
            message (Message): The message to add.

        Raises:
            ValueError: If the first message added is not from the system.
        """
        if self.has_sys_msg:
            if (len(self.messages) == 0) and (message.role != "system"):
                raise ValueError(f"First message must be from system. Your message's role was: {message.role}")

        self.messages.append(message)

    def to_list(self):
        """Converts the conversation history to a list of dictionaries.

        Returns:
            list: A list of dictionaries, each containing 'role' and 'content' keys.
        """
        return [{"role": message.role, "content": message.message} for message in self.messages]

    def populate_from_list(self, message_list: list):
        """Populates the conversation history from a list of dictionaries.

        Args:
            message_list (list): A list of dictionaries, each containing 'role' and 'content' keys.
        """
        for message in message_list:
            self.add_message(Message(message.role, message.message))

    def to_text_form(self, N: int = None) -> str:
        """Converts the conversation history to text form, omitting system messages.

        Args:
            N (int, optional): The number of messages to include in the output. Defaults to None, meaning all messages.

        Returns:
            str: The conversation history in text form.
        """
        if N is not None:
            N = min(N, len(self.messages))
        else:
            N = len(self.messages)

        conversation_text = ""
        for message in self.messages[-N:]:
            if message.role != "system":
                conversation_text += f"{message.role}: {message.message}\n"

        return conversation_text

    def copy_without_system_messages(self):
        """Creates and returns a copy of the MessageHistory without system messages.

        Returns:
            MessageHistory: A copy of the current MessageHistory instance without system messages.
        """
        # Create a new instance of MessageHistory
        copied_history = MessageHistory(has_sys_msg=False)

        # Iterate through the messages in the current instance and add non-system messages to the copied instance
        for message in self.messages:
            if message.role != "system":
                copied_history.add_message(message)

        return copied_history

    def add_system_message(self, content: str or Message):
        """Adds a system message to the beginning of the MessageHistory.

        Args:
            content (str): The content of the system message to add.
        """
        if len(self.messages) > 0 and self.messages[0].role == "system":
            raise IndexError("This Message History already has a system message!")
        else:
            system_message = content if isinstance(content, (Message)) else Message("system", content)
            self.messages.insert(0, system_message)

    def save_to_file(self, full_file_path: str):
        """Saves the conversation history to a JSON file."""
        with open(full_file_path, 'w') as f:
            json.dump(self.to_list(), f)


    def add_messages_from_twilio(self, twilio_message_list, twilio_client_name: str) -> None:
        """Populates the history from a Twilio Message History. Note: The process assumes that there are only 
        two participants in the conversation, and that the user "twilio_client_name" is the bot (assistant).

        :param twilio_message_list: Message list from executing the messages.list() function on a Twilio 
        conversation. NOTES ABOUT THIS PARAMETER:
            - It is assumed that the list is sorted from most recent to less recent. So it needs to be reverted.
            - It is assumed that conversations have an "author" and "body" attribute.
        :type twilio_message_list: client.conversations.conversations(conversation_sid).messages.list()
        :param twilio_client_name: Name of the client in Twilio. If you haven't set one, it will be the 
        combination of the type of communication, a colon, and the phone number. So, if you are using 
        whatsapp and the number is +1 (234) 5678, then it will be: "whatsapp:+12345678".
        :type twilio_client_name: str
        """
        msg_list = twilio_message_list.copy() # messages from most recent to less recent
        msg_list = msg_list[::-1] # reverted --> first message (index 0) is less recent

        for message in twilio_message_list:
            if message.author == twilio_client_name:
                role = "assistant"
            else:
                role = "user"

            message_obj = Message(role=role, message=message.body)
            self.add_message(message_obj)
        
