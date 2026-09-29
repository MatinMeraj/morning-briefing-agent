import anthropic

# --- 1. Read the input files ---
with open("tasks.txt") as f:
    tasks = f.read()

with open("schedule.txt") as f:
    schedule = f.read()

# --- 2. Build the prompt ---
today = "Monday, September 28, 2026"  # we'll automate this later

prompt = f"""You are my personal morning planning assistant.

Today is {today}.

Here are my FIXED commitments (these cannot move — work, class, sleep):
{schedule}

Here are my TASKS to fit around them:
{tasks}

Produce a morning briefing that:
1. Lists my day in priority order, using the Eisenhower matrix
   (urgent + important first). Deadlines drive urgency.
2. Respects every fixed block above — never schedule a task during
   sleep, class, or work.
3. Does NOT overload the day. If there isn't enough free time,
   say so and tell me what to defer.
4. Gives a ONE-LINE reason for each task's placement.

Format it as a clean, scannable briefing I can read in 30 seconds.
Be concise. No filler."""

# --- 3. Call Claude ---
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}],
)

# --- 4. Print the briefing ---
print(message.content[0].text)
