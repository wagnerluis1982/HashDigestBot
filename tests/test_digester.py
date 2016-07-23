import unittest

from hashdigestbot.digester import hashtags, HashMessage, Digester
from hashdigestbot.model.database import Base


class TestDigester(unittest.TestCase):
    def setUp(self):
        self.digester = Digester()
        Base.metadata.create_all()

    def tearDown(self):
        Base.metadata.drop_all()

    # set the flow as a lambda because SQLAlchemy keeps track of instances
    flow = lambda: (
        # These messages should be fed?
        HashMessage(1938, "Did you see #Superman?", 1),     # yes: message with hashtag
        HashMessage(1939, "I am an useless message", 1),    # no: without HT or a reply
        HashMessage(1940, "Yes, I saw", 1, reply_to=1938),  # yes: replying a message with HT
        HashMessage(1941, "#IronMaiden rules", 2),          # yes
        HashMessage(1942, "Oh my, they killed #Kenny", 3),  # yes
        HashMessage(1943, "Yeahhhh!!!", 2, reply_to=1941),  # yes
        HashMessage(1944, "Bastards!", 3, reply_to=1942),   # yes
    )

    def test_feed(self):
        messages = self.__class__.flow()

        digester = self.digester
        self.assertTrue(digester.feed(messages[0]))
        self.assertEqual(digester.db.get_messages("superman"), messages[0:1])

        self.assertFalse(digester.feed(messages[1]))
        self.assertEqual(digester.db.get_messages("superman"), messages[0:1])

        self.assertTrue(digester.feed(messages[2]))
        self.assertEqual(digester.db.get_messages("superman"), (messages[0], messages[2]))

    def test_digest(self):
        digester = self.digester
        flow = self.__class__.flow()
        for msg in flow:
            digester.feed(msg)

        digest = digester.digest(1)
        tag = next(digest)
        self.assertEqual(tag.id, "superman")
        self.assertCountEqual(tag.forms, ["Superman"])
        self.assertSequenceEqual(list(tag.messages), [flow[0], flow[2]])
        with self.assertRaises(StopIteration):
            next(digest)

        digest = digester.digest(2)
        tag = next(digest)
        self.assertEqual(tag.id, "ironmaiden")
        self.assertCountEqual(tag.forms, ["IronMaiden"])
        self.assertSequenceEqual(tag.messages, [flow[3], flow[5]])
        with self.assertRaises(StopIteration):
            next(digest)

        digest = digester.digest(3)
        tag = next(digest)
        self.assertEqual(tag.id, "kenny")
        self.assertCountEqual(tag.forms, ["Kenny"])
        self.assertSequenceEqual(tag.messages, [flow[4], flow[6]])
        with self.assertRaises(StopIteration):
            next(digest)

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
