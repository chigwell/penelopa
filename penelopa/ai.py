import openai
import time
import logging
import tiktoken
from mistralai.client import MistralClient

class AIClient:
    total_tokens_sent = 0
    total_tokens_received = 0

    def __init__(self, api_key, model, max_attempts=80, client_type="openai"):
        self.client_type = client_type
        if client_type == "openai":
            self.client = openai.OpenAI(api_key=api_key)
        elif client_type == "mistral":
            self.client = MistralClient(api_key=api_key)
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_attempts = max_attempts

    def count_tokens(self, text):
        return len(self.encoding.encode(text))

    def create_thread_and_run(self, user_message, assistant_id):
        tokens_sent = self.count_tokens(user_message)
        self.total_tokens_sent += tokens_sent
        logging.info(f"Tokens sent in this request: {tokens_sent}")
        total_tokens = self.total_tokens_sent + self.total_tokens_received
        logging.info(f"Total tokens used: {total_tokens}")
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": user_message}],
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        return thread, run

    def wait_for_completion(self, thread_id, run_id):
        count_attempts = 0
        while count_attempts < self.max_attempts:
            count_attempts += 1
            run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            logging.info(f"Run status: {run.status}")
            if run.status == "completed":
                return run
            if run.status == "failed":
                logging.error(f"Run failed with error: {run}")
                raise Exception("Run failed with error: {}".format(run))

            time.sleep(5)
        raise TimeoutError("Exceeded maximum attempts waiting for completion ({}).".format(self.max_attempts))

    def get_thread_messages(self, thread_id):
        data = self.client.beta.threads.messages.list(thread_id=thread_id).data
        response_text = data[0].content[0].text.value
        tokens_received = self.count_tokens(response_text)
        self.total_tokens_received += tokens_received
        logging.info(f"Tokens received in this response: {tokens_received}")
        total_tokens = self.total_tokens_sent + self.total_tokens_received
        logging.info(f"Total tokens used: {total_tokens}")
        return data
