import unittest

from hashdigestbot.digester import hashtags, HashMessage, Digester


class TestDigester(unittest.TestCase):
    def test_feed(self):
        messages = (
            # These messages should be fed?
            HashMessage(1938, "Did you see #Superman?"),     # yes: message with hashtag
            HashMessage(1939, "I am an useless message"),    # no: without HT or a reply
            HashMessage(1940, "Yes, I saw", reply_to=1938),  # yes: replying a message with HT
        )

        digester = Digester()
        self.assertTrue(digester.feed(messages[0]))
        self.assertEqual(digester.get_messages("superman"), messages[0:1])

        self.assertFalse(digester.feed(messages[1]))
        self.assertEqual(digester.get_messages("superman"), messages[0:1])

        self.assertTrue(digester.feed(messages[2]))
        self.assertEqual(digester.get_messages("superman"), (messages[0], messages[2]))

    def test_hashtags(self):
        # one tag
        self.assertEqual(hashtags("I #love GDG"), {"love"})
        # several tags
        self.assertEqual(hashtags("#first #second #third"),
                         {"first", "second", "third"})
        # when characters before and after
        self.assertEqual(hashtags("no#first yes: ?#second, no: 9#third yes: #fourth:content"),
                         {"second", "fourth"})
        # unicode tags
        self.assertEqual(hashtags("Latin: #bênção Japanese: #祝福"),
                         {"bênção", "祝福"})
        # snake case
        self.assertEqual(hashtags("something #_before #in_the_middle #after_"),
                         {"_before", "in_the_middle", "after_"})
        # strange valid cases
        self.assertEqual(hashtags("#tag1.#tag2 #tag3$#tag4"),
                         {"tag1", "tag2", "tag3", "tag4"})
        # no subtags
        self.assertEqual(hashtags("#dont#like #sub#tags"), set())
