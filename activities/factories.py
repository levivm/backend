import random
from datetime import timedelta

import factory
import factory.fuzzy
from django.utils.timezone import now
from guardian.shortcuts import assign_perm

from activities.models import Activity, SubCategory, Category, Tags, ActivityPhoto, Calendar, CalendarSession
from locations.factories import LocationFactory
from organizers.factories import OrganizerFactory

CATEGORIES = ["Arte", "Danza", "Deportes", "Estilo de vida", "Gastronomía", "Idiomas", "Música", "Niños", "Profesional",
              "Tecnología"]

SUBCATEGORIES = ['Académico', 'Acordeón', 'Actuación', 'Alemán', 'Amor y Sexo', 'Animación', 'Armónica', 'Arquitectura',
                 'Arte', 'Audio y Producción', 'Bailes', 'Bailes de Salón', 'Bajo', 'Ballet', 'Batería', 'Bebidas',
                 'Belleza', 'Boxeo', 'Campamentos', 'Canto', 'Chino', 'Cinematografía', 'Cocina', 'Comunicación',
                 'Contemporáneo', 'Costura', 'Criolla', 'DJ', 'Degustación', 'Deportes', 'Derecho',
                 'Desarrollo Web y Móvil', 'Dibujo y Pintura', 'Diseño', 'Diseño Web y Móvil', 'Docencia', 'En pareja',
                 'Entrenamiento', 'Español', 'Espiritual', 'Exótico', 'Finanzas', 'Fitness', 'Folklórico', 'Fotografía',
                 'Francés', 'Gimnasia', 'Golf', 'Guitarra', 'Habilidades', 'Idiomas', 'Ingeniería', 'Inglés',
                 'Internacional', 'Italiano', 'Japonés', 'Juegos', 'Latinas', 'Lengua de señas', 'Liderazgo',
                 'Management', 'Manejo', 'Manualidades', 'Marketing', 'Mascotas', 'Medicina', 'Microsoft', 'Moda',
                 'Modelado', 'Natación', 'Oriental', 'Otros', 'Panadería', 'Paternidad', 'Piano', 'Portugués',
                 'Programación', 'Recursos Humanos', 'Relaciones Sociales', 'Repostería', 'Saxofón', 'Startups', 'Step',
                 'Teclado', 'Tecnología', 'Tennis', 'Teoría', 'Trompeta', 'Urbano', 'Violonchelo', 'Violín', 'Yoga']


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyAttribute(lambda n: random.choice(CATEGORIES))
    color = factory.Faker('hex_color')


class SubCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubCategory

    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyAttribute(lambda n: random.choice(SUBCATEGORIES))


class TagsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tags

    @factory.lazy_attribute
    def name(self):
        counter = Tags.objects.count()
        return 'tag %d' % (counter + 1)


class ActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activity

    def __new__(cls, *args, **kwargs):
        return super(ActivityFactory, cls).__new__(*args, **kwargs)

    sub_category = factory.SubFactory(SubCategoryFactory)
    organizer = factory.SubFactory(OrganizerFactory)
    title = factory.LazyAttribute(
        lambda a: '%s de %s' % (random.choice(['Curso', 'Clase', 'Taller', 'Sesiones']), a.sub_category.name))
    short_description = factory.Faker('sentence')
    level = factory.LazyAttribute(lambda a: random.choice([k for k, v in Activity.LEVEL_CHOICES]))
    goals = factory.Faker('paragraph')
    methodology = factory.Faker('paragraph')
    content = factory.Faker('paragraph')
    audience = factory.Faker('paragraph')
    requirements = factory.Faker('paragraph')
    return_policy = factory.Faker('paragraph')
    extra_info = factory.Faker('paragraph')
    youtube_video_url = factory.Faker('url')
    location = factory.SubFactory(LocationFactory)
    score = factory.LazyAttribute(lambda a: random.choice(range(100)))

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if create and extracted:
            self.tags.add(*extracted)

    @factory.post_generation
    def instructors(self, create, extracted, **kwargs):
        if create and extracted:
            self.instructors.add(*extracted)


class ActivityPhotoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityPhoto

    photo = 'activities/blue.jpg'
    thumbnail = 'activities/thumbnail_blue.jpg'
    activity = factory.SubFactory(ActivityFactory)
    main_photo = False


class CalendarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Calendar

    activity = factory.SubFactory(ActivityFactory)
    initial_date = factory.fuzzy.FuzzyDateTime(now(), now() + timedelta(days=30))
    closing_sale = factory.LazyAttribute(lambda c: c.initial_date + timedelta(days=15))
    number_of_sessions = factory.LazyAttribute(lambda c: random.choice(range(0, 10)))
    session_price = factory.LazyAttribute(lambda c: random.choice(range(100000, 1000000)))
    capacity = factory.LazyAttribute(lambda c: random.choice(range(25)))


class CalendarSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CalendarSession

    date = factory.fuzzy.FuzzyDateTime(now() + timedelta(days=30), now() + timedelta(days=365))
    start_time = factory.fuzzy.FuzzyDateTime(now() + timedelta(days=30), now() + timedelta(days=365))
    end_time = factory.LazyAttribute(lambda cs: cs.start_time + timedelta(days=60))
    calendar = factory.SubFactory(CalendarFactory)
