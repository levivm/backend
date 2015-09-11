from model_mommy.recipe import Recipe, seq

from organizers.models import Organizer

organizer = Recipe(
    Organizer,
    user__username=seq('organizer'),
)
