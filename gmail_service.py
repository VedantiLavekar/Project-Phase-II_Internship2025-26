from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

import base64
import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# =========================
# GET SERVICE
# =========================

def get_service(creds):

    credentials = Credentials(

        token=creds["token"],

        refresh_token=creds.get(
            "refresh_token"
        ),

        token_uri=creds["token_uri"],

        client_id=creds["client_id"],

        client_secret=creds["client_secret"],

        scopes=creds["scopes"]

    )

    return build(
        "gmail",
        "v1",
        credentials=credentials
    )


# =========================
# EXTRACT BODY
# =========================

def extract_body(payload):

    text = ""

    def parse_parts(parts):

        nonlocal text

        for part in parts:

            mime = part.get(
                "mimeType",
                ""
            )

            body = part.get(
                "body",
                {}
            )

            data = body.get(
                "data"
            )
            if mime == "text/plain" and data:

                try:

                    decoded = base64.urlsafe_b64decode(
                        data
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )

                    text += decoded + " "

                except:
                    pass

            if "parts" in part:

                parse_parts(
                    part["parts"]
                )

    try:

        if payload.get(
            "body",
            {}
        ).get("data"):

            text += base64.urlsafe_b64decode(

                payload["body"]["data"]

            ).decode(

                "utf-8",
                errors="ignore"

            )

    except:
        pass

    if "parts" in payload:

        parse_parts(
            payload["parts"]
        )

    # =========================
    # CLEAN EMAIL
    # =========================

    # REMOVE HTML TAGS
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # REMOVE URLS
    text = re.sub(
        r"http\S+",
        " ",
        text
    )

    # REMOVE CSS / STYLE WORDS
    text = re.sub(
        r'\b(font|padding|margin|width|height|rgb|px|display|media|screen|color|background)\b',
        ' ',
        text,
        flags=re.IGNORECASE
    )

    # REMOVE LONG TOKENS
    text = re.sub(
        r"[A-Za-z0-9_-]{40,}",
        " ",
        text
    )

    # REMOVE EXTRA SPACES
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    # =========================
    # REMOVE JUNK LINES
    # =========================

    lines = text.split(".")

    cleaned = []

    for line in lines:

        line = line.strip()

        if len(line) < 5:
            continue

        lower = line.lower()

        # SKIP CSS / HTML JUNK
        if any(word in lower for word in [

            "font",
            "padding",
            "margin",
            "width",
            "height",
            "rgb",
            "px",
            "display",
            "media screen",
            "background",
            "color",
            "copyright"

        ]):

            continue

        cleaned.append(line)

    # =========================
    # FINAL CLEAN TEXT
    # =========================

    important_text = ". ".join(cleaned)

    important_text = important_text[:5000]

    important_text = important_text.strip()

    if not important_text:

        important_text = text[:1000]

    print("\n====================")
    print("CLEANED EMAIL TEXT:")
    print(important_text[:1500])
    print("====================\n")

    return important_text


# =========================
# FETCH EMAILS
# =========================

def get_emails_by_label(creds, label):

    try:

        service = get_service(creds)

        if (

            label == "SENT"

            or

            label == "[Gmail]/Sent Mail"

        ):

            results = service.users().messages().list(

                userId="me",

                q="in:sent",

                maxResults=20

            ).execute()

        else:

            results = service.users().messages().list(

                userId="me",

                labelIds=[label],

                maxResults=20

            ).execute()

        messages = results.get(
            "messages",
            []
        )

        emails = []

        for msg in messages:

            msg_data = service.users().messages().get(

                userId="me",

                id=msg["id"],

                format="full"

            ).execute()

            payload = msg_data.get(
                "payload",
                {}
            )

            headers = payload.get(
                "headers",
                []
            )

            subject = "No Subject"

            sender = "Unknown"

            for h in headers:

                if h["name"] == "Subject":

                    subject = h["value"]

                if h["name"] == "From":

                    sender = h["value"]

            snippet = msg_data.get(
                "snippet",
                ""
            )

            body = extract_body(
                 payload
                )

            # FALLBACK TO SNIPPET
            if (

                not body

                or

                body.strip() == ""

                or

                "No important content found" in body

            ):

                body = snippet

            emails.append({

                "id": msg["id"],

                "from": sender,

                "subject": subject,

                "snippet": snippet,

                "body": body

            })

        print(
            "EMAIL FETCH SUCCESS:",
            len(emails)
        )

        return emails

    except Exception as e:

        print(
            "FETCH EMAIL ERROR:",
            e
        )

        return []


# =========================
# SEND EMAIL
# =========================

def send_email(
    creds,
    to,
    subject,
    body
):

    service = get_service(creds)

    to = to.strip().lower()

    to = to.replace(
        " ",
        ""
    )

    to = to.rstrip("., ")

    message = MIMEText(body)

    message["to"] = to

    message["from"] = "me"

    message["subject"] = subject

    raw = base64.urlsafe_b64encode(

        message.as_bytes()

    ).decode()

    sent = service.users().messages().send(

        userId="me",

        body={
            "raw": raw
        }

    ).execute()

    print(
        "EMAIL SENT:",
        sent["id"]
    )


# =========================
# REPLY EMAIL
# =========================

# =========================
# REPLY EMAIL
# =========================

def reply_email(credentials, msg_id, reply_text):

    try:

        service = get_service(credentials)

        # GET ORIGINAL MESSAGE

        original = service.users().messages().get(

            userId="me",

            id=msg_id,

            format="metadata",

            metadataHeaders=[

                "Subject",

                "From",

                "Message-ID"

            ]

        ).execute()

        headers = original["payload"]["headers"]

        subject = ""

        to = ""

        message_id = ""

        for h in headers:

            name = h["name"]

            value = h["value"]

            if name == "Subject":

                subject = value

            elif name == "From":

                to = value

            elif name == "Message-ID":

                message_id = value

        # ADD RE PREFIX

        if not subject.startswith("Re:"):

            subject = "Re: " + subject

        from email.mime.text import MIMEText
        import base64

        message = MIMEText(reply_text)

        message["to"] = to

        message["subject"] = subject

        message["In-Reply-To"] = message_id

        message["References"] = message_id

        raw = base64.urlsafe_b64encode(

            message.as_bytes()

        ).decode()

        send_message = {

            "raw": raw,

            "threadId": original["threadId"]

        }

        result = service.users().messages().send(

            userId="me",

            body=send_message

        ).execute()

        print("REPLY SENT:", result)

        return True

    except Exception as e:

        print("REPLY ERROR:", e)

        return False


# =========================
# MOVE EMAIL TO TRASH
# =========================

def delete_email(credentials, msg_id):

    try:

        service = get_service(credentials)

        print("MOVING EMAIL TO TRASH:", msg_id)

        response = service.users().messages().trash(

            userId="me",

            id=msg_id

        ).execute()

        print("TRASH RESPONSE:", response)

        return True

    except Exception as e:

        print("GMAIL DELETE ERROR:", str(e))

        return False