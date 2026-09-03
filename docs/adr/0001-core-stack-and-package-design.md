# 0001. Core Stack and Package Design

## Status

Accepted

## Context

Project needs reliable scalable architecture for async vacancy fetching (ETL) from many sources and HTTP API maintaining.

Main challenges:

* Preventing data duplication in concurrent environment.
* High speed of DOM parsing without memory leakage.
* Isolation background processes from web layer.

## Decision

Approved following stack and package design:

* **Language / Web:** Python 3.14+, FastAPI.
* **Database / ORM:** PostgreSQL, SQLAlchemy 2.0 (async driver `asyncpg`). Used pattern *Data Mapper / Repository* for isolation domain models from SQL queries.
* **Scraping Core:** Isolated packages `fetchers` (only network requests via async `httpx` with custom exceptions handling) and `parsers` (fast HTML parsing via `selectolax` instead of slow `BeautifulSoup`).
* **Background Processing:** Background jobs rotation via `APScheduler`. DB session lifecycle hard-isolated into every job run via `async_sessionmaker`.

## Consequences

### Pros

* High parsing speed.
* Safe concurrency at the DB level due to in-memory repository deduplication.
* Clean code decomposition (easy to add new sources).

### Cons

* Async code base requires more strict transaction control in tests (`commit / flush` nuances).
