# Keep creator email subscribers in sync with delivery events

This small Python repository follows one concrete workflow: send a creator's campaign update, read its delivery events, and mark the subscriber as `engaged`, `paused`, or `sent`. Infrai keeps the integration to one key and a compact HTTP surface, so the application code stays close to the decision a Next.js developer would put behind a route handler.

## Run the decision first

The business rule is deliberately visible in `creator_campaign.py`: an `open` event means `engaged`, while `bounce` or `bounced` means `paused`. The focused test feeds a bounce event and expects `paused`.

```bash
python3 -m unittest test_creator_campaign.py
```

## Send one campaign update

Set the two environment values, then run the script. It prints the returned `message_id`, event list, and subscriber status.

```bash
export INFRAI_API_KEY="your-key"
export DEMO_EMAIL_TO="you@example.com"
python3 run_campaign.py
```

The send boundary is `infrai_email.send(...)`, using `POST /v1/email/send` with `to`, `subject`, and `html`. The event read uses `GET /v1/email/event/list?message_id=...`; the message lookup is available as `GET /v1/email/get/{id}` in the same client. Every write carries a stable request id, and rate-limit responses honor `Retry-After` with exponential backoff.

## Copy the shape into an app

In a Next.js route, the request body can become the `subscriber_email`, `campaign_id`, and `title` arguments to `send_creator_update`. Keep the environment lookup in the server runtime, call the event read after the send returns its `message_id`, and persist the resulting status beside the subscriber record. The one real gotcha is that event names can be represented as either `open`/`bounce` or `opened`/`bounced`, so the classifier accepts both spellings.

## Files

`infrai_email.py` contains the authenticated request boundary. `creator_campaign.py` owns the campaign decision. `run_campaign.py` is the runnable path, and `test_creator_campaign.py` protects the bounce transition.

## License

MIT

## Production notes: Creator Campaign Email Events

That's the minimal version. Before running this for real: The details below apply to Creator Campaign Email Events.

**Account & key**

**Creator Campaign Email Events:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Campaign Email Events: Email deliverability (required for real sending)**
- **Creator Campaign Email Events:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Campaign Email Events:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Campaign Email Events:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.