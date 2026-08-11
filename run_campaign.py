import json
import os
from creator_campaign import send_creator_update
from infrai_email import infrai_email


def main():
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("DEMO_EMAIL_TO is required")
    campaign_id = os.environ.get("CAMPAIGN_ID", "spring-studio-update")
    result = send_creator_update(infrai_email(), recipient, campaign_id, "A new note from the studio")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
