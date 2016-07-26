from django.core.management.base import BaseCommand

from activities.models import Category, SubCategory


class Command(BaseCommand):
    help = "Create categories and subcategories"

    def handle(self, *args, **options):
        self.load_categories_and_subcategories()

    def load_categories_and_subcategories(self):
        data = self.get_data()
        for category_name, value in data.items():
            subcategories = value['subcategories']
            category = Category.objects.create(name=category_name, color=value['color'])
            _subcategories = map(lambda x: SubCategory(name=x, category=category),
                                 subcategories)
            SubCategory.objects.bulk_create(_subcategories)

    @staticmethod
    def get_data():
        return {

            "Arte y Manualidades": {'color': '#46416D',
                     'subcategories': ['Actuación', 'Cinematografía', 'Costura', 'Dibujo y Pintura', 'Diseño',
                                       'Fotografía', 'Manualidades', 'Moda', 'Otros']},
            "Danza": {'color': '#38DBC7',
                      'subcategories': ['Bailes de Salón', 'Ballet', 'Contemporáneo', 'Exótico', 'Folklórico',
                                        'Latinas', 'Oriental', 'Step', 'Urbano', 'Otros']},
            "Vida Cotidiana": {'color': '#00AAD1',
                               'subcategories': ['Amor y Sexo', 'Belleza', 'Paternidad', 'Espiritual', 'Habilidades',
                                                 'Manejo',
                                                 'Mascotas', 'Relaciones Sociales', 'Yoga', 'Otros']},
            "Deportes": {'color': '#C177EF',
                         'subcategories': ['Boxeo', 'Fitness', 'Gimnasia', 'Golf', 'Natación', 'Tennis',
                                           'Otros']},
            "Gastronomía": {'color': '#EB5369',
                            'subcategories': ['Bebidas', 'Criolla', 'Internacional', 'Degustación', 'En pareja',
                                              'Panadería', 'Repostería', 'Otros']},
            "Idiomas": {'color': '#00AA79',
                        'subcategories': ['Alemán', 'Chino', 'Español', 'Francés', 'Inglés', 'Italiano', 'Japonés',
                                          'Lengua de señas', 'Portugués', 'Otros']},
            "Música": {'color': '#FF7E60',
                       'subcategories': ['Acordeón', 'Armónica', 'Audio y Producción', 'Bajo', 'Batería', 'Canto', 'DJ',
                                         'Guitarra', 'Piano', 'Saxofón', 'Teclado', 'Teoría', 'Trompeta', 'Violín',
                                         'Violonchelo', 'Otros']},
            "Infantiles": {'color': '#0084B4 ',
                      'subcategories': ['Académico', 'Actuación', 'Arte', 'Bailes', 'Campamentos', 'Cocina', 'Deportes',
                                        'Habilidades', 'Idiomas', 'Tecnología', 'Otros']},
            "Profesional": {'color': '#FFC971',
                            'subcategories': ['Académico', 'Arquitectura', 'Comunicación', 'Derecho', 'Docencia',
                                              'Entrenamiento', 'Finanzas', 'Ingeniería', 'Liderazgo', 'Management',
                                              'Marketing', 'Recursos Humanos', 'Medicina', 'Startups', 'Otros']},
            "Tecnología": {'color': '#EB9F61',
                           'subcategories': ['Animación', 'Desarrollo Web y Móvil', 'Diseño Web y Móvil', 'Juegos',
                                             'Microsoft', 'Modelado', 'Programación', 'Otros']},
            "Fitness": {'color': '#222222'},
        }
