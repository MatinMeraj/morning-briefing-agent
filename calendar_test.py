import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only access to your calendar
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_service():
    creds = None
    # token.json stores your login after the first time
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    except FileNotFoundError:
        pass

    # If no valid login, do the browser flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save for next time
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_todays_events():
    service = get_calendar_service()

    # Time window: now until end of today
    now = datetime.datetime.utcnow()
    start = now.isoformat() + "Z"
    end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    if not events:
        print("No events found for the rest of today.")
        return

    print("Today's events:")
    for event in events:
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(no title)")
        print(f"  {start_time} — {summary}")

get_todays_events()
