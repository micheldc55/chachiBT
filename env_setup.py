import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description="Create a .env file with given or default values.")
    parser.add_argument('--apikey', default="YOUR_OPENAI_KEY_HERE", help="Your OpenAI key value")
    parser.add_argument('--model', default="gpt-4", help="Your OpenAI model name")
    parser.add_argument('--embeddingmodel', default="text-embedding-ada-002", help="Your OpenAI model name")
    
    return parser.parse_args()

def create_env_file(key, model, embedding_model):
    with open("test_env/.env", "w") as file:
        file.write(f"""OPENAI_KEY="{key}"\n""")
        file.write(f"""CHAT_MODEL="{model}"\n""")
        file.write(f"""EMBEDDING_MODEL="{embedding_model}"\n""")

def file_exists(file_name):
    return os.path.isfile(file_name)

def confirm_overwrite():
    response = input(".env file already exists. Do you want to overwrite it? (y/n): ").lower().strip()
    return response == 'y'

if __name__ == "__main__":
    args = get_args()

    if file_exists(".env"):
        if not confirm_overwrite():
            print("Aborted. .env file not modified.")
            exit()

    create_env_file(args.key, args.model, args.embeddingmodel)
    print(".env file created successfully!")

