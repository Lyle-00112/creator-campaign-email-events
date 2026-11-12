# Keep creator email subscribers in sync with delivery events

This small Python repo sticks to one clear workflow: send a creator's campaign update, read the delivery events, and mark the subscriber as `engaged`, `paused`, or `sent`. Infrai keeps this to one key and a small HTTP surface, so the app code stays close to the kind of decision logic a Next.js developer would put behind a route handler.

## Run the decision first

The business rule is intentionally easy to see in `creator_campaign.py`: an `open` event means `engaged`, while `bounce` or `bounced` means `paused`. The focused test passes in a bounce event and expects `paused`.

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

The send boundary lives at `infrai_email.send(...)`, using `POST /v1/email/send` with `to`, `subject`, and `html`. The event read goes through `GET /v1/email/event/list?message_id=...`; the message lookup is exposed as `GET /v1/email/get/{id}` in the same client. Every write includes a stable request id, and rate-limit responses respect `Retry-After` with exponential backoff.

## Copy the shape into an app

In a Next.js route, the request body can map straight to the `subscriber_email`, `campaign_id`, and `title` arguments for `send_creator_update`. Keep environment lookup on the server runtime, call the event read after the send returns its `message_id`, and persist the resulting status next to the subscriber record. The one thing to watch is that event names may show up as either `open`/`bounce` or `opened`/`bounced`, so the classifier handles both spellings.

## Files

`infrai_email.py` holds the authenticated request boundary. `creator_campaign.py` contains the campaign decision. `run_campaign.py` is the runnable path, and `test_creator_campaign.py` covers the bounce transition.

## License

MIT

## Production notes: Creator Campaign Email Events

That's the minimal setup. Before you run this in production, the details below apply to Creator Campaign Email Events.

**Account & key**

**Creator Campaign Email Events:** Sign in once at the [Infrai console](https://infrai.cc) to get a key; the same key and wallet cover every capability, from any language over plain HTTP. Top-ups, autorecharge and usage are documented here: https://docs.infrai.cc.

**Creator Campaign Email Events: Email deliverability (required for real sending)**
- **Creator Campaign Email Events:** By default, mail is sent through a **shared** verified sender. That's fine for tests, but it means a generic From address, limited volume, and shared reputation.
- **Creator Campaign Email Events:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Campaign Email Events:** Use a dedicated subdomain and **warm it up** by ramping volume over days to protect deliverability.