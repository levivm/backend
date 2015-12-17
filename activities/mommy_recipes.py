import random

import time
from django.utils.timezone import utc, now, timedelta
from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key, related, seq

from activities.models import Activity, SubCategory, Category, Tags, ActivityPhoto, ActivityStockPhoto, Calendar, \
    CalendarSession
from locations.mommy_recipes import location
from organizers.mommy_recipes import organizer, instructor

fake = Faker()

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


def date_with_utc(date):
    return date.replace(tzinfo=utc)

def gen_tag():
    return 'Tag %s' % time.time()

category = Recipe(
    Category,
    name=random.choice(CATEGORIES),
    color=fake.hex_color,
)

subcategory = Recipe(
    SubCategory,
    category=foreign_key(category),
    name=random.choice(SUBCATEGORIES),
)

tag = Recipe(
    Tags,
    name=gen_tag,
)

activity = Recipe(
    Activity,
    sub_category=foreign_key(subcategory),
    organizer=foreign_key(organizer),
    tags=related(tag, tag),
    title=fake.text(max_nb_chars=50),
    short_description=fake.sentence,
    level=mommy.generators.gen_from_choices(Activity.LEVEL_CHOICES),
    goals=fake.paragraph,
    methodology=fake.paragraph,
    content=fake.paragraph,
    audience=fake.paragraph,
    requirements=fake.paragraph,
    return_policy=fake.paragraph,
    extra_info=fake.paragraph,
    youtube_video_url=fake.url,
    instructors=related(instructor, instructor),
    published=mommy.generators.gen_boolean,
    certification=mommy.generators.gen_boolean,
    location=foreign_key(location),
    score=mommy.generators.gen_integer(min_int=0, max_int=100),
)

activity_photo = Recipe(
    ActivityPhoto,
    photo=mommy.generators.gen_image_field,
    activity=foreign_key(activity),
    main_photo=mommy.generators.gen_boolean,
)

activity_stock_photo = Recipe(
    ActivityStockPhoto,
    photo=mommy.generators.gen_image_field,
    sub_category=foreign_key(subcategory),
)

calendar = Recipe(
    Calendar,
    activity=foreign_key(activity),
    # initial_date=date_with_utc(fake.date_time_this_month(after_now=True)),
    # closing_sale=date_with_utc(fake.date_time_this_month(after_now=True)),
    initial_date=now() + timedelta(days=30),
    closing_sale=now() + timedelta(days=45),
    number_of_sessions=mommy.generators.gen_integer(min_int=0, max_int=10),
    session_price=mommy.generators.gen_integer(min_int=100000, max_int=1000000),
    capacity=mommy.generators.gen_integer(min_int=0, max_int=25),
    enroll_open=mommy.generators.gen_boolean,
    is_weekend=mommy.generators.gen_boolean,
    is_free=mommy.generators.gen_boolean,
)

calendar_session = Recipe(
    CalendarSession,
    # date=date_with_utc(fake.date_time_this_month(after_now=True)),
    # start_time=date_with_utc(fake.date_time_this_month(after_now=True)),
    # end_time=date_with_utc(fake.date_time_this_month(after_now=True)),
    date=now() + timedelta(days=30),
    start_time=now() + timedelta(days=30),
    end_time=now() + timedelta(days=90),
    calendar=foreign_key(calendar),
)
