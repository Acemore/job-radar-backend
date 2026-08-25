from src.exceptions.base import JobRadarError


class FetcherError(JobRadarError):
    pass


class FetcherTimeoutError(FetcherError):
    def __init__(self, url: str, original_exception: Exception):
        self.url = url
        self.original_exception = original_exception
        super().__init__(f"Timeout fetching URL: {url}. Original: {original_exception}")


class FetcherNetworkError(FetcherError):
    def __init__(self, url, original_exception):
        self.url = url
        self.original_exception = original_exception
        super().__init__(
            f"Network error fetching URL: {url}. Original: {original_exception}"
        )
