
import json
import time
from datetime import datetime, timezone

import tiktoken
from openai import OpenAI, AsyncOpenAI

from app.config import settings
from app.reliability import log_request


# OpenRouter API clients
openai_client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)

async_openai_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)


# Example pricing - verify actual model pricing
PRICING = {
    "input": 0.15 / 1_000_000,
    "output": 0.60 / 1_000_000
}


def count_tokens(messages):
    encoding = tiktoken.get_encoding("cl100k_base")

    text = json.dumps(messages, ensure_ascii=False)

    return len(encoding.encode(text))


def calculate_cost(input_tokens, output_tokens):
    input_cost = input_tokens * PRICING["input"]
    output_cost = output_tokens * PRICING["output"]

    return input_cost + output_cost


def log_usage(model, input_tokens, output_tokens, cost):
    record = {
        "date": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": cost
    }

    with open("usage.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def ask_openai(prompt):

    messages = [
        {"role": "user", "content": prompt}
    ]

    tokens = count_tokens(messages)

    if tokens > settings.max_input_tokens:
        raise ValueError("Input token limit exceeded")

    start = time.perf_counter()

    try:
        response = openai_client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages
        )

        elapsed = time.perf_counter() - start

        answer = response.choices[0].message.content

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        cost = calculate_cost(
            input_tokens,
            output_tokens
        )

        log_usage(
            settings.openrouter_model,
            input_tokens,
            output_tokens,
            cost
        )

        log_request("success", elapsed)

        print("Answer:", answer)
        print("Model:", settings.openrouter_model)
        print("Input Tokens:", input_tokens)
        print("Output Tokens:", output_tokens)
        print("Total Tokens:", input_tokens + output_tokens)
        print("Estimated Cost:", cost)
        print("Response Time:", elapsed)

        return answer

    except Exception as e:
        elapsed = time.perf_counter() - start

        log_request("failed", elapsed, error=e)

        print("API Error:", str(e))

        raise


def ask_claude(prompt, system):

    start = time.perf_counter()

    try:
        response = openai_client.chat.completions.create(
            model="anthropic/claude-3.5-haiku",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        elapsed = time.perf_counter() - start

        answer = response.choices[0].message.content

        log_request("success", elapsed)

        print("Answer:", answer)
        print("Model: anthropic/claude-3.5-haiku")

        return answer

    except Exception as e:
        elapsed = time.perf_counter() - start

        log_request("failed", elapsed, error=e)

        print("API Error:", str(e))

        raise
