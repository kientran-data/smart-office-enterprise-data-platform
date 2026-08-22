-- ============================================================
-- SMART OFFICE
-- Reset Historical Transactions
-- ============================================================

TRUNCATE TABLE
    access.access_events,
    meeting.bookings,
    signing.signing_requests,
    signing.documents,
    iot.device_events
RESTART IDENTITY;
