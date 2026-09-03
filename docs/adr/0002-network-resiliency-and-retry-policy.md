# 0002. Network Resiliency and Retry Policy

## Status

Accepted

## Context

The project requires stable, continuous operation regardless of transient network failures and external API instability.

Main challenges:

* High network instability when fetching data from external job boards.
* Flaky integration tests caused by mutating network states.
* Redundant `try / except` code duplication across different fetcher modules.

## Decision

* Implemented a custom parametrized asynchronous decorator `@retry` to handle execution retries.
* Introduced a base domain exception `FetcherError` alongside its specific subclasses: `FetcherNetworkError` and `FetcherTimeoutError`.
* Moved raw HTTP client exception mapping directly into fetchers to convert third-party errors into domain exceptions.
* Isolated test environments via fixtures to prevent real network calls during test execution.

## Consequences

### Pros

* High fault tolerance against transient infrastructure and network glitches.
* Clean DRY code layout inside background job orchestrators.
* Clean separation of concerns between network communication and domain logic.

### Cons

* Requires strict attention to the ordering of `httpx` exception handling inside both the decorator and fetcher functions.
