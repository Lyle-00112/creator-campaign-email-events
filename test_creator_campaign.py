import unittest
from unittest.mock import Mock

from creator_campaign import send_creator_update, subscriber_status


class CreatorCampaignTest(unittest.TestCase):
    def test_bounce_pauses_subscriber_after_event_read(self):
        client = Mock()
        client.send.return_value = {"message_id": "msg-42"}
        client.event_list.return_value = [{"type": "bounce"}]

        result = send_creator_update(client, "reader@example.com", "launch-7", "Studio notes")

        self.assertEqual(result["status"], "paused")
        client.event_list.assert_called_once_with("msg-42")
        client.send.assert_called_once_with(
            {"to": "reader@example.com", "subject": "Studio notes", "html": "<h1>Studio notes</h1><p>launch-7</p>"},
            request_id="creator-update:launch-7:reader@example.com",
        )


if __name__ == "__main__":
    unittest.main()
