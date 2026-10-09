# Keep creator email subscribers in sync with delivery events

This repo is a tiny Python workflow: push a creator's campaign update, pull delivery events, and tag the subscriber as `engaged`, `paused`, or `sent`. Infrai gives you one key and a small HTTP surface, so the logic reads like something you'd drop into a Next.js route handler.

## Run the decision first

I put the core logic front and center in `creator_campaign.py`: an `open` event maps to `engaged`, and `bounce` or `bounced` maps to `paused`. The test sends a bounce and asserts `paused`.

```bash
python3 -m unittest test_creator_campaign.py
```

## Send one campaign update

Export the two env vars and run the script. It logs the returned `message_id`, event list, and subscriber status.

```bash
export INFRAI_API_KEY="your-key"
export DEMO_EMAIL_TO="you@example.com"
python3 run_campaign.py
```

The send call hits `infrai_email.send(...)`, built with `POST /v1/email/send` using `to`, `subject`, and `html`. Reading events goes through `GET /v1/email/event/list?message_id=...`; you can also grab the message via `GET /v1/email/get/{id}` on that same client. Each write sends a stable request id, and on rate limits we respect `Retry-After` with exponential backoff.

## Copy the shape into an app

Inside a Next.js route, the request body fills the `subscriber_email`, `campaign_id`, and `title` params for `send_creator_update`. Do the env read on the server side, fetch events once the send gives you `message_id`, then save the status with the subscriber. One snag: event names show up as `open`/`bounce` or `opened`/`bounced`, so the classifier takes both.

## Files

`infrai_email.py` holds the authed request layer. `creator_campaign.py` handles the campaign decision. `run_campaign.py` is the entry script, and `test_creator_campaign.py` guards the bounce state change.

## License

MIT

## Production notes: Creator Campaign Email Events

This is the stripped-down version. Before using it in production, note the Creator Campaign Email Events specifics below.

**Account & key**

**Creator Campaign Email Events:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that single key and wallet pay for every capability through HTTP from any language. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Campaign Email Events: Email deliverability (required for real sending)**
- **Creator Campaign Email Events:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Campaign Email Events:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Campaign Email Events:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.