from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import sqlite3
import time

# Twilio Credentials (replace with your credentials)
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
whatsapp_from = 'whatsapp:+14155238886'  # Twilio Sandbox WhatsApp number
call_from = '+1234567890'  # Your Twilio phone number for calls
whatsapp_to = 'whatsapp:+919876543210'  # Your WhatsApp number (or the user's number)

client = Client(account_sid, auth_token)

# Initialize the scheduler
scheduler = BackgroundScheduler()

# SQLite database to store reminders
def init_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders 
                 (id INTEGER PRIMARY KEY, message TEXT, time TEXT, method TEXT)''')
    conn.commit()
    conn.close()

# Function to store a reminder in the database
def add_reminder(message, time, method):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("INSERT INTO reminders (message, time, method) VALUES (?, ?, ?)", (message, time, method))
    conn.commit()
    conn.close()

# Function to retrieve all reminders
def get_reminders():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reminders")
    reminders = c.fetchall()
    conn.close()
    return reminders

# Function to send a WhatsApp message
def send_whatsapp_message(reminder):
    message = client.messages.create(
        body=reminder[1],
        from_=whatsapp_from,
        to=whatsapp_to
    )
    print(f"WhatsApp Reminder Sent: {message.sid}")

# Function to make a voice call
def make_voice_call(reminder):
    call = client.calls.create(
        to=whatsapp_to,  # To the user's phone number
        from_=call_from,
        url='http://twimlets.com/message?Message%5B0%5D=' + reminder[1]  # Text to be read out
    )
    print(f"Call Reminder Initiated: {call.sid}")

# Function to schedule a reminder (either via WhatsApp or call)
def schedule_reminder():
    reminders = get_reminders()  # Retrieve reminders from the database
    for reminder in reminders:
        reminder_time = reminder[2]
        if reminder[3] == 'whatsapp':
            scheduler.add_job(send_whatsapp_message, 'date', run_date=reminder_time, args=[reminder])
        elif reminder[3] == 'call':
            scheduler.add_job(make_voice_call, 'date', run_date=reminder_time, args=[reminder])

# Initialize the database
init_db()

# Example of adding a new reminder
# You can call this function with different messages, times, and methods
add_reminder('Reminder to call John', '2025-03-14 15:00:00', 'whatsapp')
add_reminder('Reminder to check email', '2025-03-14 15:05:00', 'call')

# Schedule the reminders
schedule_reminder()

# Start the scheduler
scheduler.start()

# Keep the script running to allow background jobs to execute
try:
    while True:
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
