import unittest

from hashdigestbot.digester import hashtags


class TestDigester(unittest.TestCase):
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
