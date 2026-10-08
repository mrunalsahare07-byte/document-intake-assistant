# Verification & Testing Guide

This guide details how to verify the Document Intake Assistant across both backend services and the frontend client interface.

---

## 1. Backend Verification

### Starting the Server

```bash
cd backend
python -m venv .venv

# Activate environment
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

Specifying `--host 0.0.0.0` allows requests from local network devices (e.g. testing mobile responsiveness or network clients) using your local IPv4 address.

---

## 2. Automated Test Suite

Run the full pytest suite:

```bash
cd backend
pytest -v
```

This verifies:
- Single-message and multi-message field extractions
- Any-order input processing
- Correction and field-clearing intents
- Contradiction guards and clarification triggering
- Pydantic schema validation against valid and malformed payload fixtures
- Markdown document generator formatting and placeholder handling

---

## 3. Manual API Testing

Base URL: `http://localhost:8000/api`

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{ "status": "ok" }
```

### Chat Turn: Initial Details

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-01",
    "message": "My name is John Doe, living at 12 High Street, London"
  }'
```

**Expected Response:**
- Returns `ConversationResponse` with `full_name` as `"John Doe"` and `home_address` as `"12 High Street, London"`.
- Both fields marked `"confirmed"` in `field_statuses`.
- Assistant follows up with the next uncollected intake field (asset scope or children).

### Chat Turn: Asset Scope & Family

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-01",
    "message": "worldwide assets, and I do not have children"
  }'
```

**Expected Response:**
- `covers_worldwide_assets` set to `true`.
- `has_children` set to `false`, `children_names` set to `[]`.
- Assistant proceeds to ask for executor appointment.

### Chat Turn: Executor Nomination

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-01",
    "message": "My executor is my sister Sarah Doe"
  }'
```

**Expected Response:**
- `executor.name` set to `"Sarah Doe"`.
- `executor.relationship` set to `"sister"`.

### Retrieve Session State

```bash
curl -X GET http://localhost:8000/api/state/test-session-01
```

**Expected Response:**
- Returns the complete accumulated state, conversation transcript, and rendered Markdown document for `test-session-01`.

### Direct Field Correction

```bash
curl -X POST http://localhost:8000/api/correct \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-01",
    "field_name": "home_address",
    "value": "42 Elm Street, Oxford"
  }'
```

**Expected Response:**
- Overwrites `home_address` to `"42 Elm Street, Oxford"` and recalculates the Markdown document.

### Reset Session

```bash
curl -X POST http://localhost:8000/api/reset/test-session-01
```

**Expected Response:**
- Clears session state and returns a fresh intake transcript with initial greeting.

---

## 4. Postman / Insomnia Setup

To test endpoints in Postman:

1. Create a new Collection named **Document Intake Assistant**.
2. Add a Collection Variable `base_url` set to `http://localhost:8000`.
3. Add the following requests:
   - `GET {{base_url}}/health`
   - `POST {{base_url}}/api/chat` with JSON body `{"sessionId": "test-1", "message": "My name is John Doe"}`
   - `GET {{base_url}}/api/state/test-1`
   - `POST {{base_url}}/api/correct` with JSON body `{"sessionId": "test-1", "field_name": "home_address", "value": "New Address"}`
   - `POST {{base_url}}/api/reset/test-1`

---

## 5. Frontend Client Verification

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

### Verification Checklist:
1. **Interactive Chat**: Enter messages in the chat composer; verify responses appear in the conversation pane.
2. **Live State Updates**: Check the middle pane as information is provided; verified items update status badges to `Confirmed`.
3. **Markdown Rendering**: Confirm the right pane displays structured Markdown with document headers, sections, and placeholders for unprovided fields.
4. **Session Management**: Use the sidebar to create new intake sessions and switch between active records.
5. **Session Reset**: Click **Reset Session** in the top navigation bar to reset the intake to its initial state.
