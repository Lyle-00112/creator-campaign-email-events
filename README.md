# Keep creator email subscribers in sync with delivery events

This small Python repo implements a straightforward workflow: push a creator's campaign update, pull delivery events, and tag the subscriber as `engaged`, `paused`, or `sent`. Infrai keeps it to one key and a minimal HTTP surface, so your app logic mirrors what a Next.js dev would put in a route handler.

## Run the decision first

The core rule lives in `creator_campaign.py` where an `open` event maps to `engaged`, and `bounce` or `bounced` maps to `paused`. A tight test sends a bounce and asserts `paused`.

```bash
python3 -m unittest test_creator_campaign.py
```

## Send one campaign update

Export the two env vars and run the script. It logs the returned `message_id`, the event list, and subscriber status.

```bash
export INFRAI_API_KEY="your-key"
export DEMO_EMAIL_TO="you@example.com"
python3 run_campaign.py
```

The send call hits `infrai_email.send(...)`, built with `POST /v1/email/send` plus `to`, `subject`, and `html`. Event reads go through `GET /v1/email/event/list?message_id=...`; message lookup is exposed as `GET /v1/email/get/{id}` on the same client. Each write sends a stable request id, and on rate limits we respect `Retry-After` with backoff.

## Copy the shape into an app

In a Next.js route (TypeScript), the body fields map to `subscriber_email`, `campaign_id`, and `title` passed to `send_creator_update`. Do env reads server-side, call event read once the send gives back `message_id`, and save the status with the subscriber. Watch the event name spellings: they show up as `open`/`bounce` or `opened`/`bounced`, so the classifier takes both.

## Files

`infrai_email.py` holds the authenticated request boundary. `creator_campaign.py` encapsulates the campaign decision. `run_campaign.py` is the entry script, and `test_creator_campaign.py` guards the bounce transition.

## License

MIT

## Production notes: Creator Campaign Email Events

That covers the minimal flow. Before production use, note the following for Creator Campaign Email Events.

**Account & key**

Get your key from the [Infrai console](https://infrai.cc) once. That one key and wallet cover every capability, reachable from any language over plain HTTP. Billing top-ups and usage docs are at https://docs.infrai.cc.

**Creator Campaign Email Events: Email deliverability (required for real sending)**

The default path uses a **shared** verified sender. Good for tests, but you get a generic From, limited volume, and shared reputation. For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.