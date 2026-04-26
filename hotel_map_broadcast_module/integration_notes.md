# Hotel Map & Broadcast Module — Integration Notes

## 🔗 Purpose
Defines how this module integrates into the main CrisisBridge-AI system.

## 1. Alert System Integration
Currently, the module uses a dedicated `BroadcastManager` with WebSockets.
**Later:**
- Replace `manager.broadcast()` in `broadcast_service.py` with `alert_service.trigger()`.
- Use the main system's notification delivery mechanism.

## 2. Authentication Integration
**Currently:**
- No authentication (hardcoded "admin").
**Later:**
- Wrap routes with `Depends(require_role(UserRole.ADMIN))`.
- Use `get_current_user` to populate `uploaded_by` and `created_by`.

## 3. Dashboard Integration
- Broadcast messages should appear in the main guest/staff dashboard.
- Maps will be used for visual guidance during incidents.

## 4. Incident Integration
- Link broadcasts to specific incidents.
- Add `incident_id` to `broadcast_messages` table.

## 5. Storage Migration
- Move `FileHandler` to use Cloud Storage (GCS/S3) instead of local filesystem.

## 6. Scaling
- Replace in-memory `BroadcastManager` with Redis Pub/Sub for multi-instance support.
