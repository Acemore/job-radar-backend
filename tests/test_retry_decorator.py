from src.exceptions.fetcher import FetcherError
from src.utils.retry import retry


async def test_retry_decorator_success():
    call_count = 0

    @retry(attempts=3, delay=0.001)
    async def fake_api_call():
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            raise FetcherError("Network glitch")

        return {"status": "ok"}

    result = await fake_api_call()

    assert result == {"status": "ok"}
    assert call_count == 3
