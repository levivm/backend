from activities.models import SubCategory, ActivityStockPhoto
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create categories and subcategories covers photo"

    MAPPING = {
        "Arte": {
            "Actuación": 5,
            "Cinematografía": 5,
            "Costura": 5,
            "Dibujo y Pintura": 5,
            "Diseño": 5,
            "Fotografía": 5,
            "Manualidades": 5,
            "Moda": 5,
            "Otros": 1,
        },
        "Danza": {
            "Bailes de Salón": 5,
            "Ballet": 5,
            "Contemporáneo": 5,
            "Exótico": 5,
            "Folklórico": 5,
            "Latinas": 5,
            "Oriental": 5,
            "Otros": 5,
            "Step": 5,
            "Urbano": 5,
        },
        "Deportes": {
            "Boxeo": 5,
            "Fitness": 5,
            "Gimnasia": 5,
            "Golf": 5,
            "Natación": 5,
            "Otros": 5,
            "Tennis": 5,
        },
        "Estilo de vida": {
            "Amor y Sexo": 5,
            "Belleza": 5,
            "Espiritual": 5,
            "Habilidades": 5,
            "Manejo": 5,
            "Mascotas": 5,
            "Otros": 5,
            "Paternidad": 5,
            "Relaciones Sociales": 5,
            "Yoga": 5,
        },
        "Gastronomía": {
            "Bebidas": 5,
            "Criolla": 5,
            "Degustación": 5,
            "En pareja": 5,
            "Internacional": 5,
            "Otros": 5,
            "Panadería": 5,
            "Repostería": 5,
        },
        "Idiomas": {
            "Alemán": 5,
            "Chino": 5,
            "Español": 5,
            "Francés": 5,
            "Inglés": 5,
            "Italiano": 5,
            "Japonés": 5,
            "Lengua de señas": 5,
            "Otros": 5,
            "Portugués": 5,
        },
        "Música": {
            "Acordeón": 5,
            "Armónica": 5,
            "Audio y Producción": 5,
            "Bajo": 5,
            "Batería": 5,
            "Canto": 5,
            "DJ": 5,
            "Guitarra": 5,
            "Otros": 5,
            "Piano": 5,
            "Saxofón": 5,
            "Teclado": 5,
            "Teoría": 5,
            "Trompeta": 5,
            "Violín": 5,
            "Violonchelo": 5,
        },
        "Niños": {
            "Académico": 5,
            "Actuación": 5,
            "Arte": 5,
            "Bailes": 5,
            "Campamentos": 5,
            "Cocina": 5,
            "Deportes": 5,
            "Habilidades": 5,
            "Idiomas": 5,
            "Otros": 5,
            "Tecnología": 5,
        },
        "Profesional": {
            "Académico": 5,
            "Arquitectura": 5,
            "Comunicación": 5,
            "Derecho": 5,
            "Docencia": 5,
            "Entrenamiento": 5,
            "Finanzas": 5,
            "Ingeniería": 5,
            "Liderazgo": 5,
            "Management": 5,
            "Marketing": 5,
            "Medicina": 5,
            "Otros": 5,
            "Recursos Humanos": 5,
            "Startups": 5,
        },
        "Tecnología": {
            "Animación": 5,
            "Desarrollo Web y Móvil": 5,
            "Diseño Web y Móvil": 5,
            "Juegos": 5,
            "Microsoft": 5,
            "Modelado": 5,
            "Otros": 5,
            "Programación": 5
        }
    }

    def handle(self, *args, **options):
        subcategories = SubCategory.objects.all()

        for subcategory in subcategories:
            category = subcategory.category
            try:
                self.MAPPING[category.name][subcategory.name]
            except KeyError:

                pass
            for index in range(1, self.MAPPING[category.name][subcategory.name] + 1):
                data = {
                    'category': category.name,
                    'subcategory': subcategory.name,
                    'filename': '%s %02i.jpg' % (subcategory.name.lower(), index)
                }
                filepath = 'activities_stock/%(category)s/%(subcategory)s/%(filename)s' % data
                ActivityStockPhoto.objects.create(sub_category=subcategory, photo=filepath)
