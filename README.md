Week 5 – LLM Application Development
Project: Company Chat Service
Overview

A secured company chat backend built using Python, OpenAI SDK, Anthropic SDK and FastAPI.

Features
OpenAI and Anthropic SDK integration.
Streaming responses using Server-Sent Events.
Token counting and API cost tracking.
Tenacity retry mechanism with exponential backoff.
Async API calls using asyncio.gather.
Semaphore-based concurrency control.
Function calling with three custom tools.
Parallel tool execution and error handling.
Conversation history and summarisation.
Token-budget management.
FastAPI session management.
API key authentication.
Pydantic validation and CORS.
Pytest automated testing.
Run the application
bash
pip install -r requirements.txt
uvicorn app.main:app --reload

Run tests
bash
pytest -v

Check coverage
bash
pytest --cov=app --cov-report=html

Security decisions
API keys are loaded from environment variables.
Secrets are never committed to Git.
secrets.compare_digest is used for API-key comparison.
Protected routes require authentication.
Errors are returned in a consistent JSON structure.
Design decisions
Async calls improve throughput.
Exponential backoff handles temporary API failures.
Conversation summarisation reduces token usage.
Semaphore limits concurrent API requests.
Dependency injection makes testing easier.
Limitations

The assessment version uses in-memory sessions and illustrative cost rates. Production deployment requires persistent storage, current provider pricing, accurate provider-specific token accounting and production-grade logging.