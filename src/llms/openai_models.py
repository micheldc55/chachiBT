import logging
from typing import List

import numpy as np
import openai
import pandas as pd
import tiktoken
import torch
from tenacity import retry, stop_after_attempt, wait_exponential

import sys
sys.path.append('/workspace/')
from src.messages.messages import Message, MessageHistory


def log_retry(retry_state):
    logging.error(f"Retrying: {retry_state.attempt_number}...")
    logging.error(f"Exception: {retry_state.outcome.exception()}")


class TokenCounter:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.encoding = tiktoken.encoding_for_model(model)

    def encode(self, messages: List[str] or str) -> List[List[int]]:
        if isinstance(messages, str):
            messages = [messages]

        return self.encoding.encode_batch(messages)

    def decode(self, tokens: List[List[int]] or List[int]):
        if isinstance(tokens[0], int):
            tokens = [tokens]

        return self.encoding.decode_batch(tokens)


class OpenAiChat:
    def __init__(self, history: MessageHistory, model: str = "gpt-3.5-turbo-0613", temperature: float = 0.0):
        self.model = model
        self.history = history
        self.temperature = temperature

    def __call__(self, prompt: str):
        """Call the OpenAI chat API with the prompt and return the response."""
        new_message = Message("user", prompt)
        self.history.add_message(new_message)

        response = openai.ChatCompletion.create(
            messages=self.history.to_list(),
            model=self.model,
            temperature=self.temperature,
        )
        return response


class OpenAiChatWithRetries:
    def __init__(self, history: MessageHistory, model: str = "gpt-3.5-turbo-0613", temperature: float = 0.0):
        self.model = model
        self.history = history
        self.temperature = temperature

    def __call__(self, prompt: str, temperature: float or None = None, retries: int = 5, base_wait: int = 5):
        """Call the OpenAI chat API with the prompt and return the response."""
        if isinstance(prompt, str):
            new_message = Message("user", prompt)
        elif isinstance(prompt, Message):
            new_message = prompt
        else:
            raise TypeError(f"Prompt must be of the type str or Message. You passed: {type(prompt)}")

        self.history.add_message(new_message)

        if temperature is None:
            temperature = self.temperature

        # apply the retry decorator with the desired arguments (waits are in miliseconds)
        @retry(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=base_wait, max=20),
            before_sleep=log_retry,
        )
        def predict():
            response = openai.ChatCompletion.create(
                messages=self.history.to_list(),
                model=self.model,
                temperature=temperature,
            )
            return response

        response = predict()

        return response

    def predict_on_messages(self, message_history: MessageHistory, temperature: float or None = None):
        """Call the OpenAI model on a Message History instead of a message"""
        if temperature is None:
            temperature = self.temperature

        response = openai.ChatCompletion.create(
            messages=message_history.to_list(),
            model=self.model,
            temperature=temperature,
        )

        return response


class OpenAiChatWithFunctionCallingAndRetries:
    def __init__(
            self, 
            history: MessageHistory, 
            functions: list,
            function_call: str = "auto",
            model: str = "gpt-3.5-turbo-0613", 
            temperature: float = 0.0
        ):

        self.model = model
        self.history = history
        self.temperature = temperature
        self.functions = functions
        self.function_call = function_call

    def __call__(self, prompt: str, temperature: float or None = None, retries: int = 5, base_wait: int = 5):
        """Call the OpenAI chat API with the prompt and return the response."""
        if isinstance(prompt, str):
            new_message = Message("user", prompt)
        elif isinstance(prompt, Message):
            new_message = prompt
        else:
            raise TypeError(f"Prompt must be of the type str or Message. You passed: {type(prompt)}")

        self.history.add_message(new_message)

        if temperature is None:
            temperature = self.temperature

        # apply the retry decorator with the desired arguments (waits are in miliseconds)
        @retry(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=base_wait, max=20),
            before_sleep=log_retry,
        )
        def predict():
            response = openai.ChatCompletion.create(
                messages=self.history.to_list(),
                model=self.model,
                temperature=temperature,
                functions=self.functions, 
                function_call=self.function_call
            )
            return response

        response = predict()

        return response

    def predict_on_messages(self, message_history: MessageHistory, temperature: float or None = None):
        """Call the OpenAI model on a Message History instead of a message"""
        if temperature is None:
            temperature = self.temperature

        response = openai.ChatCompletion.create(
            messages=message_history.to_list(),
            model=self.model,
            temperature=temperature,
            functions=self.functions, 
            function_call=self.function_call
        )

        return response


class OpenAiCompletion:
    pass


class OpenAiEmbeddings:
    def __init__(self, model: str = "text-embedding-ada-002"):
        self.model = model
        # self.embedding = openai.Embeddings(model)

    def embed_text(self, messages: List[str] or str):
        model = self.model

        if isinstance(messages, str):
            messages = [messages.replace("\n", " ")]
        else:
            messages = [message.replace("\n", " ") for message in messages]

        return openai.Embedding.create(input=messages, model=model)

    @staticmethod
    def get_embeddings_list(openai_response: dict):
        data = openai_response["data"]  # list
        return [item["embedding"] for item in data]

    @staticmethod
    def get_torch_embeddings(openai_response: dict):
        data = openai_response["data"]  # list
        return torch.stack([torch.tensor(item["embedding"]) for item in data])

    @staticmethod
    def get_numpy_embeddings(openai_response: dict):
        data = openai_response["data"]
        list_arrays = [np.array(item["embedding"]) for item in data]
        return np.array(list_arrays)


def get_openai_models(name_contains: str = "gpt-3.5-turbo-0613"):
    """List all models with name containing `name_contains` in openai.Model.list()

    Note: you must run the following commands first for an API key stored in a .env file:
    import os
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    """
    model_list = openai.Model.list()
    model_list_out = []

    for model in model_list["data"]:
        if name_contains in model["id"]:
            model_list_out.append(model)

    return model_list_out


if __name__ == "__main__":
    import os

    import openai
    from dotenv import load_dotenv

    from src.file_parsers.output_parsers import openai_response_parser, openai_function_call_response_parser

    load_dotenv()

    openai.api_key = os.getenv("OPENAI_KEY")

    # models = get_openai_models("3.5")

    # print(models)

    history = MessageHistory()

    fake_sys_msg = Message(role="system", message="Eres un asistente muy simpático")
    user_message = Message(role="user", message="Hola, podrias ayudarme con una pregunta que tengo?")
    assistant_message = Message(role="assistant", message="Hola, soy MIKKA! Soy un chatbot entrenado por la empresa para responder a tus dudas sobre RR.HH. En qué puedo ayudarte hoy?")
    history.populate_from_list([fake_sys_msg, user_message, assistant_message])
    messages = history.to_list()

    functions = [
        {
            "name": "get_company_name",
            "description": "Get the company name", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "bot_name": {
                        "type": "string", 
                        "description": "The name of the bot in lowercase letters"
                    }, 
                    "unit": {"type": "string"},
                }, 
                "required": ["bot_name"]
            }
        }
    ]

    user_msg = "Cual es el nombre de la empresa del bot?"
    messages.append({"role": "user", "content": user_msg})

    chat = OpenAiChatWithFunctionCallingAndRetries(
        history, functions, "auto"
    )

    response_dict = chat(user_msg)
    response, _ = openai_function_call_response_parser(response_dict)

    # chat = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     functions=functions,
    #     function_call="auto",
    #     temperature=0.2
    # )

    print(response)