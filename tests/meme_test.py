import unittest

from impl.meme import skill, INTENT_NAME


class TestMeme(unittest.TestCase):

    def test_meme_handler(self):
        """ A simple test case to ensure that our implementation returns 'RANDOM_MEME_AFFIRMATION'
        """
        response = skill.test_intent(INTENT_NAME)
        self.assertEqual(response.text.key, 'RANDOM_MEME_AFFIRMATION')
