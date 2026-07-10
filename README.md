# Resilient API Data Extractor (Python + `requests`)

A Python project demonstrating how to build a **resilient, production-style
API client** from the ground up — reusable HTTP sessions, automatic retries
with exponential backoff and jitter, timeout handling, and memory-efficient
streaming extraction — applied to two different pagination strategies
(offset-based and cursor-based).

The core engineering focus of this project is **not pagination** — it's
building a reliable API integration layer. Pagination is included as two
interchangeable strategies (`offset_extractor.py` and `cursor_extractor.py`)
to show the resiliency layer working correctly regardless of how the target
API paginates its results.

---

## Core focus: building a resilient API client

Any script can call `requests.get()`. This project focuses on what it takes
to call an API *reliably* in a real-world setting:

### 1. Persistent HTTP session
A single `requests.Session()` is created once per `ApiExtractor` instance and
reused across every call, instead of opening a new TCP/TLS connection per
request:

```python
self.session = requests.session()
self.session.headers.update({
    "x-api-key": f"{self.api_token}",
    "Accept": "application/json",
    "X-Reqres-Env": "prod"
})
```

### 2. Retry logic with exponential backoff + jitter
`_request_with_retry()` wraps every HTTP call and centralizes error handling
so it doesn't need to be duplicated at every call site:

```python
if response.status_code >= 500:  # server error
    delay = 2 ** attempt + random.uniform(0, 1)  # exponential backoff + jitter
    print(f"Server error {response.status_code}. Retrying in {delay:.1f}s")
    time.sleep(delay)
    continue
```

- **Exponential backoff** (`2 ** attempt`) — each retry waits longer than the
  last, giving a struggling server time to recover instead of hammering it.
- **Jitter** (`random.uniform(0, 1)`) — a small random delay is added on top
  so that if many clients get rate-limited or hit an error at the same time,
  they don't all retry in perfect lockstep and cause a "thundering herd"
  spike on the server.
- Retries are capped at 5 attempts, after which a `RuntimeError` is raised
  rather than retrying forever.

### 3. Timeouts on every request
Every request carries an explicit `timeout` so a stalled connection can't
hang the whole extraction run indefinitely.

### 4. Memory-safe streaming extraction
`ExtractAll()` is written as a **generator** — it `yield`s one page of
records at a time instead of accumulating the full result set in memory:

```python
with open("output/output_data.json", 'a') as f:
    for record in extractor.ExtractAll(endpoint="records", param=...):
        f.write(json.dumps(record) + "\n")
```

This means the script's memory footprint stays flat whether the API returns
10 pages or 10,000 — records are written to disk as they arrive.

### 5. Secure configuration
API credentials are loaded from a `.env` file via `python-dotenv`, keeping
secrets out of source control.

---

## Pagination strategies

The same resilient `ApiExtractor` foundation is applied to two different
pagination mechanisms, showing the retry/session/streaming logic is
independent of *how* the API paginates:

| | `offset_extractor.py` | `cursor_extractor.py` |
|---|---|---|
| **Strategy** | Client tracks a `page`/`limit` and increments it each call | Server returns a `next_cursor` that the client passes back on the next call |
| **Loop condition** | Stops when the API returns an empty `data` array | Stops when the API stops returning a `next_cursor` |
| **State carried between calls** | Integer offset (`param["page"] += limit`) | Opaque cursor token (`param["cursor"] = next_cursor`) |
| **Typical use case** | Small/static datasets, random page access | Large or frequently-changing datasets |

---

## Project structure

```
.
├── offset_extractor.py     # Offset/page-based pagination
├── cursor_extractor.py     # Cursor-based pagination
├── output/
│   └── output_data.json    # Extracted records (JSON Lines, one page per line)
├── .env                    # API_KEY=your_key_here  (not committed)
└── requirements.txt
```

---

## Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd <repo-name>
pip install -r requirements.txt
```

`requirements.txt`:
```
requests
python-dotenv
```

**2. Configure your API key**

Create a `.env` file in the project root:

```
API_KEY=your_api_key_here
```

**3. Run either extractor**

```bash
python offset_extractor.py
python cursor_extractor.py
```

Each run appends extracted pages as JSON Lines to `output/output_data.json`.

---

## Design notes

- **`ApiExtractor`** is intentionally generic: `base_url`, `api_token`, and
  `page_size` are constructor arguments, and `ExtractAll(endpoint, param)`
  takes the endpoint and initial query params — so the same class can target
  different endpoints or APIs without modification.
- **`_request_with_retry`** centralizes all HTTP error handling in one place,
  so both pagination strategies benefit from the same resiliency logic
  without duplicating it.
- Choosing a **generator** for `ExtractAll` was deliberate: for APIs that
  return thousands of pages, loading everything into a list before writing
  would be memory-inefficient. Streaming page-by-page to the output file
  keeps the process lightweight.

---

## Known limitations / next steps

This project is a working proof of concept, and there are a few things I'd
tighten up before calling it production-ready:

- No structured logging (currently `print` statements) — would swap for the
  `logging` module with configurable log levels.
- No unit tests yet — the retry/backoff logic and the two pagination loops
  are good candidates for tests with a mocked `requests.Session`.
- No handling for `4xx` client errors beyond `raise_for_status()` — could add
  more granular handling (e.g., re-authenticating on `401`).

---

## Tech stack

- Python 3
- `requests` — HTTP client with session support
- `python-dotenv` — environment variable management

---

# Note
This Project uses free API proved by ReqRes which support feature like pagination, Authorization, etc. It is very simple to use and has a detailed implementation step on their page.
You can check out here: https://app.reqres.in/

*This project was built as a hands-on exercise in designing a resilient API
integration layer — session reuse, retry logic with exponential backoff and
jitter, timeouts, and streaming extraction — and validating it against two
real-world pagination strategies.*