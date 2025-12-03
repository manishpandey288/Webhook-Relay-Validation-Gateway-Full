# Webhook Gateway Dashboard

A minimal single-page HTML/CSS/JavaScript dashboard for the Webhook Gateway system.

## Features

- **Metrics Dashboard**: Shows total delivered, failed, pending, dead letters, and success rate
- **Recent Events**: Lists recent webhook events with status and actions
- **Dead-Letter Queue**: Displays failed events that can be replayed
- **Event Attempts**: View detailed attempt history for any event
- **Tenant Filtering**: Filter events by tenant ID
- **Auto-refresh**: Automatically refreshes every 30 seconds

## Usage

1. **Start the backend server:**
   ```bash
   python main.py
   ```

2. **Open the dashboard:**
   - Simply open `dashboard.html` in your web browser
   - Or serve it with a simple HTTP server:
     ```bash
     # Python 3
     python -m http.server 8080
     
     # Then open: http://localhost:8080/dashboard.html
     ```

## Features

### Metrics Cards
- Total Delivered (green)
- Total Failed (red)
- Pending (yellow)
- Dead Letters (red)
- Success Rate (percentage)

### Recent Events Table
- Event ID, Tenant ID, Event Type
- Status badges (delivered/failed/pending/processing)
- Retry count
- Created timestamp
- Actions: View Attempts, Replay

### Dead-Letter Queue Table
- Failed event details
- Failure reason
- Replay button (disabled if already replayed)

### Event Attempts
- Click "View Attempts" on any event to see:
  - Attempt number
  - Status (success/failed)
  - Response code
  - Error message
  - Retry delay
  - Timestamp

## API Endpoints Used

- `GET /admin/metrics` - Get system metrics
- `GET /admin/events` - List recent events
- `GET /admin/events/{id}/attempts` - Get event attempt history
- `POST /admin/replay/{id}` - Replay a failed event
- `GET /admin/dead-letters` - Get dead-letter queue

## Notes

- The dashboard uses vanilla JavaScript (no frameworks)
- All styling is in a single HTML file
- CORS is enabled on the backend to allow API calls
- Auto-refreshes every 30 seconds
- Tenant filter is populated from recent events

