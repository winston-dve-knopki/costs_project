# Project Coding Rules (Non-Obvious Only)
- Always use async database sessions (AsyncSession)
- Transaction endpoints currently hardcode user_id=1
- Date parameters in API endpoints are static - recompute per request
- Use custom type shortcuts (int_pk, str_255) for model definitions
- The updated_dttm field is database-managed - don't set manually