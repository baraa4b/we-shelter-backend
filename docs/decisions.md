# Design decisions

- **FastAPI** — type-driven request/response validation, native async, and built-in OpenAPI keep the route layer thin without giving up on safety.
- **MongoDB + Beanie** — documents fit the animal/adoption/note shape better than relational rows, and Beanie's Pydantic-flavored async modeling pairs cleanly with FastAPI's request schemas with minimal glue.
- **JWT (access + refresh)** — stateless auth, no session store needed. Short-lived access tokens (30 min default) limit blast radius; refresh tokens (7 days) keep the UX usable. Token kind lives in a `typ` claim, so an access token cannot be replayed at `/auth/refresh` and vice versa.
- **Images in a separate collection with binary subtype** — keeps the `animals` collection small for listing queries and gives images their own lifecycle (upload validation, cascade delete). GridFS would be overkill for a hard 1 MB-per-file ceiling.
- **Two-repo split** — this repo is backend-only; the Vite + React frontend lives in its own repo and consumes the API over CORS. Both deploy independently and can be reviewed without dragging in the other half.
- **No Docker** — Railway's Nixpacks builder handles Python from `requirements.txt` natively. A Dockerfile would be one more moving part for a project of this size with no payoff.
- **Smoke tests only** — the suite covers the public contract end-to-end (auth → CRUD → adoption lifecycle) through httpx. Unit-testing every service function wouldn't catch the bugs that actually matter here (wire-format drift, layering violations, broken happy paths). Deeper integration tests can be added when the API hardens.
