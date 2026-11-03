
import time
import json
from datetime import datetime, timezone

from app.llm import openai_client, count_tokens, calculate_cost, log_usage
from app.config import settings
from app.reliability import log_request


def stream_openai(prompt):

    messages = [
        {"role": "user", "content": prompt}
    ]

    input_tokens = count_tokens(messages)

    if input_tokens > settings.max_input_tokens:
        raise ValueError("Input token limit exceeded")

    start = time.perf_counter()
    first_token = True

    output_text = ""

    try:
        stream = openai_client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )

        for chunk in stream:

            if not chunk.choices:
                if chunk.usage:
                    input_tokens = chunk.usage.prompt_tokens
                    output_tokens = chunk.usage.completion_tokens
                continue

            content = chunk.choices[0].delta.content

            if content:

                if first_token:
                    print(
                        "Time to first token:",
                        round(time.perf_counter() - start, 2)
                    )
                    first_token = False

                output_text += content

                yield content

        elapsed = time.perf_counter() - start

        if not output_tokens:
            output_tokens = count_tokens([
                {"role": "assistant", "content": output_text}
            ])

        cost = calculate_cost(input_tokens, output_tokens)

        log_usage(
            settings.openrouter_model,
            input_tokens,
            output_tokens,
            cost
        )

        log_request("success", elapsed)

        print("Model:", settings.openrouter_model)
        print("Input Tokens:", input_tokens)
        print("Output Tokens:", output_tokens)
        print("Total Tokens:", input_tokens + output_tokens)
        print("Estimated Cost:", cost)
        print("Response Time:", elapsed)

    except Exception as e:

        elapsed = time.perf_counter() - start

        log_request("failed", elapsed, error=e)

        print("Streaming Error:", str(e))

        raise
