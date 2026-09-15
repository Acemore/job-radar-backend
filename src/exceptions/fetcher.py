from src.exceptions.base import JobRadarError


class FetcherError(JobRadarError):
    pass


class FetcherNetworkError(FetcherError):
    def __init__(self, url, original_exception):
        self.url = url
        self.original_exception = original_exception
        super().__init__(
            f"Network error fetching URL: {url}. Original: {original_exception}"
        )
