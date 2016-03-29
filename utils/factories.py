import factory

from utils.models import CeleryTaskEditActivity


class CeleryTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CeleryTaskEditActivity

    task_id = factory.Faker('uuid4')
