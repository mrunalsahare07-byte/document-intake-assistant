# Production Improvements

This project is a submission / demo-quality implementation. If this were to
be hardened for real production use, the following improvements would be
made:

## Backend
- **Persistence**: Replace the in-memory `SessionStore` with a real
  database (PostgreSQL / Redis) so sessions survive server restarts and
  scale across multiple instances.
- **Authentication**: Add user authentication/authorization so each user
  can only access their own sessions and documents.
- **Real LLM integration**: Swap `MockLLMService` for a real provider
  (OpenAI, Azure OpenAI, Anthropic) behind the existing `LLMService`
  interface, with proper prompt engineering, retries, and rate limiting.
- **Input validation & security**: Add request size limits, stricter
  Pydantic validation, and sanitize all free-text fields before rendering
  in Markdown/HTML to prevent injection.
- **Error handling & logging**: Centralized structured logging (e.g. with
  correlation IDs per session) and consistent error responses instead of
  relying on default FastAPI error pages.
- **CORS**: Restrict `allow_origins` to specific known frontend domains
  instead of `"*"`.
- **Rate limiting**: Protect the `/api/chat` endpoint from abuse.
- **Async LLM calls**: Use async HTTP clients for real LLM providers so the
  API doesn't block under load.

## Frontend
- **Code splitting**: Address the "chunk larger than 500kB" build warning
  using dynamic imports / manualChunks to reduce initial bundle size.
- **Error boundaries & loading states**: More robust UX for network
  failures, retries, and empty states.
- **Accessibility**: Full a11y audit (ARIA labels, keyboard navigation,
  color contrast).
- **Testing**: Add frontend unit/integration tests (e.g. Vitest + React
  Testing Library) - currently only the backend has automated tests.
- **Environment configuration**: Externalize the API base URL via
  environment variables instead of a hardcoded `/api` proxy path.


## Data & Compliance
- **Data retention policy**: Since this collects sensitive personal
  information (wills/wishes), a real product would need encryption at
  rest, audit logging, and a clear data retention/deletion policy.
- **Legal review**: Actual legal review of generated document content and
  disclaimers, since this current version is explicitly fictional/demo
  content only.

