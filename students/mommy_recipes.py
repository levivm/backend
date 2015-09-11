from model_mommy.recipe import Recipe, seq

from students.models import Student

student = Recipe(
    Student,
    user__username=seq('student'),
)
