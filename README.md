# Voice Register Cliniko Backend

A FastAPI backend that wraps Cliniko operations behind REST endpoints. It is designed to support LLM-driven tool integration for:

1. Booking an appointment
2. Retrieving patient details
3. Searching available booking information across branches

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and update values:

```bash
copy .env.example .env
```

3. Set `CLINIKO_API_KEY` and `BRANCH_LOCATION_MAP` in `.env`.

## Running

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Book an appointment
POST `/appointments/book`

Body:
- `patient_id`: Cliniko patient ID
- `appointment_type_id`: Cliniko appointment type ID
- `branch_name`: Configured branch key from `BRANCH_LOCATION_MAP`
- `starts_at`: ISO date/time string
- `note`: optional note
- `practitioner_id`: optional provider ID

### Retrieve patient details
GET `/patients/{patient_id}`

### Search availability
GET `/availability`

Query parameters:
- `branch_name` (optional)
- `start_date` (required)
- `end_date` (required)

## Notes

- The backend is intentionally built as standard REST APIs so you can expose them to an LLM as tool actions.
- `BRANCH_LOCATION_MAP` must map your app branch names to Cliniko `location_id` values.
- The current availability search returns booked appointments in the requested branch and date range.
