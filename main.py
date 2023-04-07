import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import pickle
import time
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import openai

# Gmail API setup
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Load environment variables from the .env file
load_dotenv()

# Set the OpenAI API key from the environment variable
open_ai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = open_ai_api_key

# Load the credentials from the token.pickle file, or create a new one if not present
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

# Build the Gmail API client with the provided credentials
gmail = build("gmail", "v1", credentials=creds)

# Function to list all unread emails in the user's Gmail inbox
def list_emails():
    # Fetch unread emails using Gmail API
    results = gmail.users().messages().list(userId="me", q="is:unread").execute()
    emails = results.get("messages", [])
    return emails

# Function to read the subject and message of a given email
def read_email(email_id):
    # Fetch email using Gmail API
    msg = gmail.users().messages().get(userId="me", id=email_id).execute()
    headers = msg["payload"]["headers"]

    # Extract email subject from headers
    subject = next((header["value"] for header in headers if header["name"].lower(
    ) == "subject"), "No Subject")
    message = ""

    # Extract email message content
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                message = base64.urlsafe_b64decode(
                    part["body"]["data"]).decode("utf-8")
                break
    elif msg["payload"]["mimeType"] == "text/plain":
        message = base64.urlsafe_b64decode(
            msg["payload"]["body"]["data"]).decode("utf-8")

    return subject, message

# Function to generate a draft response for a given prompt using OpenAI Chat API
def generate_response(prompt):
    conversation = [
        {"role": "system", "content": "You are an email drafting expert. You are given an email subject and body. You must write a draft response to the email."},
        {"role": "user", "content": prompt}
    ]

    # Send the conversation to OpenAI Chat API and get the generated response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=150,
        temperature=0.5
    )

    return response.choices[0].message["content"].strip()

# Function to create a draft in Gmail with the given subject and message text
def create_draft(subject, message_text):
    message = MIMEMultipart()
    text = MIMEText(message_text, "plain")
    message.attach(text)
    message["subject"] = subject
    create_message = {"message": {
        "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}}

    try:
        draft = gmail.users().drafts().create(userId="me", body=create_message).execute()
        print(f"Draft id: {draft['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

# Main function that continuously checks for new emails and processes them
def main():
    while True:
        emails = list_emails()
        if not emails:
            print("No new emails.")
        else:
            for email in emails:
                email_id = email["id"]
                subject, message = read_email(email_id)
                prompt = f"Email subject: {subject}\nEmail body: {message}\nSuggest a draft response:"
                draft_response = generate_response(prompt)
                new_subject = f"Re: {subject}"
                create_draft(new_subject, draft_response)

                # Mark email as read
                gmail.users().messages().modify(
                    userId="me",
                    id=email_id,
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()
                print(f"Email {email_id} processed and marked as read.")

        # Sleep for a certain time (e.g., 5 minutes) before checking for new emails again
        time.sleep(300)


if __name__ == "__main__":
    main()
