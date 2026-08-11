"""Business workflow: deliver a creator update, then classify its events."""

from infrai_email import InfraiEmail

# The application-facing idiom is infrai_email.send(...), backed by this client.


def send_creator_update(client: InfraiEmail, subscriber_email: str, campaign_id: str, title: str):
    result = client.send(
        {"to": subscriber_email, "subject": title, "html": f"<h1>{title}</h1><p>{campaign_id}</p>"},
        request_id=f"creator-update:{campaign_id}:{subscriber_email}",
    )
    message_id = result["message_id"]
    events = client.event_list(message_id)
    return {"message_id": message_id, "status": subscriber_status(events), "events": events}


def subscriber_status(events):
    names = {event.get("type") for event in events}
    if "bounce" in names or "bounced" in names:
        return "paused"
    if "open" in names or "opened" in names:
        return "engaged"
    return "sent"
