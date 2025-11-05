# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Database Connection
- Always use async sessions (AsyncSession)
- The DATABASE_URL falls back to a local development string if not set in environment
- Database setup is in `src/database/database.py`

## Migrations
- Alembic must be run from project root directory
- Migration command: `alembic upgrade head`
- Included in Docker startup sequence

## API Conventions
- user_id is currently hardcoded to 1 in transaction endpoints
- Date parameters in transactions endpoint are module-level and don't update
- Date parameters are passed as strings but compared as datetime objects

## Models
- Uses custom type shortcuts: int_pk, str_255
- updated_dttm is automatically managed by the database
- Transaction model stores raw_text which might contain unparsed data

## Project Structure
- Database models in `src/database/models.py`
- Database schemas in `src/common/schemas.py`
- API endpoints in `src/api/` package