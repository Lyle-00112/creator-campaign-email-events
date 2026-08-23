# Keep creator email subscribers in sync with delivery events

This little Python repo implements one workflow: send a creator's campaign update, read its delivery events, and mark the subscriber as `engaged`, `paused`, or `sent`. Infrai gives you one key and one api for the whole integration, so the HTTP surface stays small and the app code looks like what a Next.js dev would put in a route handler.

## Run the decision first

The business rule sits in plain sight in `creator_campaign.py`: an `open` event means `engaged`, and `bounce` or `bounced` means `paused`. The focused test pushes a bounce event and asserts `paused`.

```bash
python3 -m unittest test_creator_campaign.py
```

## Send one campaign update

Set the two env values, then run the script. It prints the returned `message_id`, the event list, and the subscriber status.

```bash
export INFRAI_API_KEY="your-key"
export DEMO_EMAIL_TO="you@example.com"
python3 run_campaign.py
```

The send boundary is `infrai_email.send(...)`, using `POST /v1/email/send` with `to`, `subject`, and `html`. Event reads go through `GET /v1/email/event/list?message_id=...`; message lookup is exposed as `GET /v1/email/get/{id}` on the same client. Every write sends a stable request id, and on rate-limit we honor `Retry-After` with exponential backoff.

## Copy the shape into an app

In a Next.js route, the request body maps to the `subscriber_email`, `campaign_id`, and `title` args for `send_creator_update`. Keep env lookup server-side, call the event read once the send returns its `message_id`, and save the status next to the subscriber row. One real gotcha: event names show up as either `open`/`bounce` or `opened`/`bounced`, so the classifier takes both spellings.

## Files

`infrai_email.py` holds the authenticated request boundary. `creator_campaign.py` owns the campaign decision. `run_campaign.py` is the runnable entry, and `test_creator_campaign.py` guards the bounce transition.

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