def openai_response_parser(response: dict) -> tuple:
    """Function that takes an openai dict response and parses it.

    :param response: The response dictionary directly obtained from the openai.ChatCompletion.create endpoint.
    :type response: dict
    :return: Returns a tuple of single response (str) and the dictionary of token counts.
    :rtype: tuple
    """
    text_response = response["choices"][0]["message"]["content"]
    token_dict = response["usage"]

    return text_response, token_dict


def openai_function_call_response_parser(response: dict) -> tuple:
    """Function that takes an openai dict response and parses it.

    :param response: The response dictionary directly obtained from the openai.ChatCompletion.create endpoint.
    :type response: dict
    :return: Returns a tuple of single response (str) and the dictionary of token counts.
    :rtype: tuple
    """
    message_dict = response["choices"][0]["message"]

    if "function_call" in message_dict:
        function_name = message_dict["function_call"]["name"]
        function_args = message_dict["function_call"]["arguments"]
        message_content = None
        
    else:
        function_name = None
        function_args = None
        message_content = message_dict["content"]

    response_dict = {"message_content": message_content, "function_name": function_name, "function_params": function_args}
    token_dict = response["usage"]
        
    return response_dict, token_dict
