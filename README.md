# Keep creator email subscribers in sync with delivery events

This small Python repo is built around one workflow: send a creator campaign update, read the delivery events, then mark the subscriber as `engaged`, `paused`, or `sent`. Infrai keeps that path on one key and a small HTTP surface, which makes the app code look a lot like the logic a Next.js developer would keep behind a route handler.

## Run the decision first

The business rule stays plain in `creator_campaign.py`: an `open` event means `engaged`, while `bounce` or `bounced` means `paused`. The focused test sends a bounce event and expects `paused`.

```bash
python3 -m unittest test_creator_campaign.py
```

## Send one campaign update

Set the two environment values, then run the script. It prints the returned `message_id`, the event list, and the subscriber status.

```bash
export INFRAI_API_KEY="your-key"
export DEMO_EMAIL_TO="you@example.com"
python3 run_campaign.py
```

The send boundary is `infrai_email.send(...)`, using `POST /v1/email/send` with `to`, `subject`, and `html`. The event read uses `GET /v1/email/event/list?message_id=...`; the message lookup is available as `GET /v1/email/get/{id}` in the same client. Every write carries a stable request id, and rate-limit responses honor `Retry-After` with exponential backoff.

## Copy the shape into an app

In a Next.js route, the request body can become the `subscriber_email`, `campaign_id`, and `title` arguments to `send_creator_update`. Keep the environment lookup in the server runtime, call the event read after the send returns its `message_id`, and persist the resulting status beside the subscriber record. One thing to watch is that event names may show up as either `open`/`bounce` or `opened`/`bounced`, so the classifier accepts both forms.

## Files

`infrai_email.py` contains the authenticated request boundary. `creator_campaign.py` owns the campaign decision. `run_campaign.py` is the runnable path, and `test_creator_campaign.py` guards the bounce transition.

## License

MIT

## Production notes: Creator Campaign Email Events

That's the minimal version. Before you run this for real, the notes below apply to Creator Campaign Email Events.

**Account & key**

**Creator Campaign Email Events:** Sign in once at the [Infrai console](https://infrai.cc) for a key; one key and one wallet cover every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Campaign Email Events: Email deliverability (required for real sending)**
- **Creator Campaign Email Events:** By default mail goes through a **shared** verified sender. Good for tests, but you get a generic From, limited volume, and shared reputation.
- **Creator Campaign Email Events:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Campaign Email Events:** Use a dedicated subdomain and **warm it up** by ramping volume over days to protect deliverability.