from activities.models import SubCategory, ActivityStockPhoto
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create categories and subcategories covers photo"

    MAPPING = {
        "Arte": {
            "Actuación": 9,
            "Cinematografía": 6,
            "Costura": 9,
            "Dibujo y Pintura": 14,
            "Diseño": 14,
            "Fotografía": 15,
            "Manualidades": 5,
            "Moda": 8,
            "Otros": 1
        },
        "Danza": {
            "Bailes de Salón": 5,
            "Ballet": 13,
            "Contemporáneo": 10,
            "Exótico": 9,
            "Folklórico": 5,
            "Latinas": 7,
            "Oriental": 6,
            "Otros": 13,
            "Step": 12,
            "Urbano": 7
        },
        "Deportes": {
            "Boxeo": 7,
            "Fitness": 37,
            "Gimnasia": 10,
            "Golf": 7,
            "Natación": 15,
            "Otros": 10,
            "Tennis": 7
        },
        "Estilo de vida": {
            "Amor y Sexo": 5,
            "Belleza": 17,
            "Espiritual": 8,
            "Habilidades": 29,
            "Manejo": 6,
            "Mascotas": 7,
            "Otros": 3,
            "Paternidad": 8,
            "Relaciones Sociales": 5,
            "Yoga": 21
        },
        "Gastronomía": {
            "Bebidas": 20,
            "Criolla": 9,
            "Degustación": 17,
            "En pareja": 8,
            "Internacional": 24,
            "Otros": 16,
            "Panadería": 15,
            "Repostería": 17
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
            "Portugués": 5
        },
        "Música": {
            "Acordeón": 5,
            "Armónica": 5,
            "Audio y Producción": 12,
            "Bajo": 7,
            "Batería": 6,
            "Canto": 10,
            "DJ": 7,
            "Guitarra": 20,
            "Otros": 9,
            "Piano": 11,
            "Saxofón": 10,
            "Teclado": 5,
            "Teoría": 5,
            "Trompeta": 7,
            "Violín": 16,
            "Violonchelo": 5
        },
        "Niños": {
            "Académico": 5,
            "Actuación": 5,
            "Arte": 6,
            "Bailes": 5,
            "Campamentos": 5,
            "Cocina": 6,
            "Deportes": 6,
            "Habilidades": 7,
            "Idiomas": 7,
            "Otros": 18,
            "Tecnología": 8
        },
        "Profesional": {
            "Académico": 5,
            "Arquitectura": 5,
            "Comunicación": 9,
            "Derecho": 7,
            "Docencia": 8,
            "Entrenamiento": 6,
            "Finanzas": 6,
            "Ingeniería": 9,
            "Liderazgo": 7,
            "Management": 7,
            "Marketing": 7,
            "Medicina": 6,
            "Otros": 4,
            "Recursos Humanos": 6,
            "Startups": 7
        },
        "Tecnología": {
            "Animación": 5,
            "Desarrollo Web y Móvil": 5,
            "Diseño Web y Móvil": 5,
            "Juegos": 5,
            "Microsoft": 10,
            "Modelado": 6,
            "Otros": 3,
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
            print (category.name,subcategory.name)
            for index in range(0, self.MAPPING[category.name][subcategory.name]):
                data = {
                    'category': category.name,
                    'subcategory': subcategory.name,
                    'filename': '%s%i.jpg' % (subcategory.name, index)
                }
                filepath = '%(category)s/%(subcategory)s/%(filename)s' % data
                ActivityStockPhoto.objects.create(sub_category=subcategory, photo=filepath)
