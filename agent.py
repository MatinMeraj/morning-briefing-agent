import datetime
from zoneinfo import ZoneInfo
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import anthropic

# ---------- CONFIG ----------
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TIMEZONE = ZoneInfo("America/Vancouver")

# ---------- GOOGLE CALENDAR ----------
def get_calendar_service():
    creds = None
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    except FileNotFoundError:
        pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_todays_events():
    service = get_calendar_service()

    # Local "now" and local end-of-day, converted to UTC for the API
    now_local = datetime.datetime.now(TIMEZONE)
    end_local = now_local.replace(hour=23, minute=59, second=59, microsecond=0)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now_local.isoformat(),
        timeMax=end_local.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    # Format events into clean text lines for the prompt
    lines = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "(no title)")
        # Trim the timestamp to just HH:MM if it's a timed event
        if "T" in start:
            time_part = start.split("T")[1][:5]
            lines.append(f"{time_part} — {summary}")
        else:
            lines.append(f"All day — {summary}")

    return "\n".join(lines) if lines else "No fixed events left today."

# ---------- TASKS ----------
def get_tasks():
    with open("tasks.txt") as f:
        return f.read()

# ---------- CLAUDE BRIEFING ----------
def build_briefing(schedule, tasks):
    today = datetime.datetime.now(TIMEZONE).strftime("%A, %B %d, %Y")

    prompt = f"""You are my personal morning planning assistant.

Today is {today}.

Here are my FIXED commitments pulled live from my calendar (cannot move):
{schedule}

Here are my TASKS to fit around them:
{tasks}

Produce a morning briefing that:
1. Lists my day in priority order using the Eisenhower matrix
   (urgent + important first). Deadlines drive urgency.
2. Respects every fixed block above — never schedule a task during
   sleep, class, or work.
3. Uses ONLY the commitments listed above. Do not invent events.
4. Does NOT overload the day. If free time is short, say what to defer.
5. Gives a ONE-LINE reason for each task's placement.

Format it as a clean, scannable briefing I can read in 30 seconds.
Be concise. No filler."""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

# ---------- MAIN ----------
def main():
    print("Pulling your calendar...\n")
    schedule = get_todays_events()
    tasks = get_tasks()
    briefing = build_briefing(schedule, tasks)
    print(briefing)

main()
