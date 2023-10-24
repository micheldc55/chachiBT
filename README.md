# chachiBT
Implements a simple ChatGPT equivalent with streamlit that also records your conversations.

## Set up

The .devcontainer folder already contains everything needed to be run using the DevContainers extension in VS Code. You have to create a file called ".env" in the main directory and it has to contain the API key to connect to OpenAI. You can get that [here](https://platform.openai.com/overview). 

I've created an easy way to create that environment file by running the file "env_setup.py". Running this file will automatically create the .env file with deafault credentials that you will need to change manually. The file can be run from the terminal. Just open a new terminal located in the main directory and run:

```python
python env_setup.py
```

This will create the file in the main directory. If you are feeling like a pro, you can set up the credentials on that same execution using the following syntax:

```python
python env_setup.py --apikey "YOUR_ACTUAL_OPENAI_KEY" --model "YOUR_ACTUAL_OPENAI_MODEL" --embeddingmodel "YOUR_EMBEDDING_MODEL"
```

Note that the keys should be passed as strings wrapped in quoatations ("). All keys are optional, except for the apikey one. If you don't set it up during execution, you need to manually update your API key. The other keys default to standard models from OpenAI.

**Default Values for the keys:**

- **model:** gpt-4
- **embeddingmodel:** text-embedding-ada-002
