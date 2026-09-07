1. **Create `backend/core/resilience.py`**
   - Implement `CircuitBreaker` and `with_retry_sync` decorators in `backend/core/resilience.py`.
   - `CircuitBreaker`: state machine that trips on successive failures, allowing fast failure when dependencies are down, and periodically retrying after a cooldown.
   - `with_retry_sync`: simple retry decorator with exponential backoff for synchronous functions.

2. **Wrap external AI calls with Resilience decorators**
   - Modify `backend/services/ai_deep_scan.py` to wrap the `chat_completion` call (and the local ollama check if useful).
   - Modify `backend/services/ollama_scan.py` to wrap `requests.post`.
   - Modify `backend/services/openclaw_agent.py` to wrap `requests.get`.

3. **Wrap External Communication (SMS/Email) with Resilience decorators**
   - Modify `backend/services/notifier.py` to wrap Twilio `client.messages.create` with retry.
   - Modify `backend/api/auth.py` to wrap Twilio and Sendgrid calls with retry.

4. **Verify Recovery Mechanisms**
   - Verify the python code syntax and run unit tests if any.

5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
   - Call `pre_commit_instructions` tool.

6. **Submit PR**
   - Commit the changes and submit the PR.
