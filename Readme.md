Danish Javed Dar - BSCS23187

# PDC Assignment 2: Secure AI App Resilience

This repository contains the backend implementation for the Distributed Systems assignment. I chose to address **Problem 3: Fault Tolerance** by implementing the Circuit Breaker pattern.

## What Was Implemented

1. **Mandatory Header Middleware**
   A global FastAPI middleware was added to `app.py` to intercept all HTTP requests and inject the `X-Student-ID: BSCS23187` header into the response, satisfying the strict submission guidelines.

2. **The Circuit Breaker Pattern**
   To prevent external AI API timeouts from exhausting the server's thread pool, a custom `CircuitBreaker` class was implemented.
   - It wraps the synchronous LLM API call in `routes/challenge.py`.
   - If the AI service fails 3 times, the circuit "opens."
   - While open, incoming requests are instantly rejected with a `503 Service Unavailable` fallback message, protecting the server until the reset timeout expires.

3. **Environment & Dependency Fixes**
   Fixed several "beyond top-level package" relative import errors and identified the unlisted dependencies required to get the base codebase running locally.

## How to Run the Server

1. Navigate to the backend source directory:
   ```bash
   cd backend/src
Install the required dependencies:

Bash
python -m pip install fastapi uvicorn sqlalchemy pydantic requests python-dotenv openai svix clerk-backend-api
Start the application:

Bash
python -m uvicorn app:app --reload
How to Run the Demo Test
While the server is running, open a second terminal window in the backend/src directory and run the test script:

Bash
python test_failure.py
This script intentionally spams the endpoint to simulate an AI outage. You will see the first three requests fail normally, and the fourth request will successfully trip the Circuit Breaker, returning the instant fallback message.