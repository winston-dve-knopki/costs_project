# Project Debug Rules (Non-Obvious Only)
- Database URL falls back to local dev string if not set
- API date parameters don't update after server start
- Database migrations must run before app startup (see Dockerfile)
- Transaction user_id is hardcoded to 1