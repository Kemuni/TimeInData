from typing import Dict

from app.types.activity_types import ActivityTypes

ACTIVITY_TO_EMOJI: Dict[ActivityTypes, str] = {
    ActivityTypes.SLEEP: '🛏️',
    ActivityTypes.WORK: '💵',
    ActivityTypes.STUDY: '🏫',
    ActivityTypes.FAMILY: '👪',
    ActivityTypes.FRIENDS: '👥',
    ActivityTypes.RELAX: '💆‍♂️',
    ActivityTypes.SPORT: '💪',
    ActivityTypes.GAMES: '🎮',
}
