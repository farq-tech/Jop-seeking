#!/usr/bin/env python3
"""Send one job application via Resend (farq.sa) with the CV attached.

Usage: send_resend.py <to> <subject> <body_file>
Refuses to send to a recipient already in the sent log. Every send is BCC'd
to the sender so a copy lands in Gmail. The API key and log live outside the
(public) repository.
"""
import base64, csv, datetime, json, os, sys, urllib.request

SCRATCH = os.environ.get("CAMPAIGN_DIR", os.path.expanduser("~/.job-campaign"))
KEY = open(os.path.join(SCRATCH, ".resend_key")).read().strip()
LOG = os.path.join(SCRATCH, "sent_log.csv")
CV = os.path.expanduser("~/Desktop/Abdulrhman_Alnuqaydan_CV_v2.pdf")
SENDER = "Abdulrhman Alnuqaydan <abdulrhman@farq.sa>"


def already_sent(to):
    if not os.path.exists(LOG):
        return False
    with open(LOG) as f:
        return any(r["to"].lower() == to.lower() for r in csv.DictReader(f))


def main():
    to, subject, body_file = sys.argv[1:4]
    if already_sent(to):
        print(f"SKIP duplicate {to}")
        return
    body = open(body_file).read()
    payload = {
        "from": SENDER,
        "to": [to],
        "bcc": ["abdulrhman@farq.sa"],
        "reply_to": "abdulrhman@farq.sa",
        "subject": subject,
        "text": body,
        "attachments": [{
            "filename": "Abdulrhman_Alnuqaydan_CV.pdf",
            "content": base64.b64encode(open(CV, "rb").read()).decode(),
        }],
    }
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "User-Agent": "farq-campaign/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.load(r)
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "to", "subject", "channel", "id"])
        if new:
            w.writeheader()
        w.writerow({"date": datetime.datetime.now().isoformat(timespec="seconds"), "to": to,
                    "subject": subject, "channel": "resend", "id": resp.get("id", "")})
    print(f"SENT {to} id={resp.get('id')}")


if __name__ == "__main__":
    main()
