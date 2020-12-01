import random

from skill_sdk import skill, Response, tell, Card
from skill_sdk.l10n import _

INTENT_NAME = 'TEAM_00_RANDOM_MEME'

RANDOM_MEME_BASE_URL = "https://bc88fvx6y8.execute-api.eu-central-1.amazonaws.com/staging/"
RANDOM_MEMES = [
    "1606586642301.jpg",
    "1606637010653.jpg",
    "1606562466592.jpg",
    "1606585220632.jpg",
    "1606583102743.jpg",
    "1606562370963.jpg",
    "1606557412334.jpg",
    "1606603385668.jpg"
]


def get_random_meme_url() -> str:
    """
    Gives a random

    :return:
    """
    return RANDOM_MEME_BASE_URL + random.choice(RANDOM_MEMES)


@skill.intent_handler(INTENT_NAME)
def handler() -> Response:
    """
    This handler is the first point of contact when your utterance is actually resolved!
    It will make sure to send you funny memes to your phone.

    :return:        Response
    """
    # We get a translated message
    msg = _('RANDOM_MEME_AFFIRMATION')
    # We create a simple response
    response = tell(msg)
    response.card = Card(
        type_="GENERIC_DEFAULT",
        title=_("RANDOM_MEME_TITLE"),
        sub_title=_("RANDOM_MEME_SUB_TITLE"),
        action=get_random_meme_url(),
        action_text=_("RANDOM_MEME_ACTION_TEXT")
    )

    return response
