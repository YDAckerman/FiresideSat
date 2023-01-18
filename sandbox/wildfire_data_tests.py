import unittest
import WildFireAPI


class WildfireTestMethods(unittest.TestCase):

    def test_wildfire_incidents(self):

        def cum_sum(x):
            return([sum(x[0:i:1]) for i in range(1, len(x)+1)])

        updated, outdated, current = WildFireAPI.test()
        # all incidents are resolved in the timeframe
        self.assertEqual(sum(updated), 32, "Should be 32")
        self.assertEqual(sum(outdated), 32, "Should be 32")
        # current incidents should equal the element-wise difference
        # of the cumulative sums of updated and outdated incidents
        self.assertEqual([i - j for i, j in zip(cum_sum(updated),
                                                cum_sum(outdated))],
                         current, "Should be equal")


if __name__ == '__main__':
    unittest.main()
