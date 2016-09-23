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
            "Arte": {'color': '#46416D',
                     'subcategories': ['Dibujo y Pintura', 'Moda', 'Fotografía', 'Diseño gráfico', 'Modelaje', 'Otros' ]},
            "Danza": {'color': '#38DBC7', 
                      'subcategories': ['Ballet', 'Arabe',  'Salsa', 'Hip Hop', 'Moderna y Contemporánea', 'Bachata', 'Rumba', 
                                        'Flamenco', 'Tap', 'Social', 'Espiritual', 'Otros Urbanos', 'Otros']
                     },
            "Manualidades": {'color': '#6B10C9', 
                      'subcategories': ['Joyería', 'Bisutería',  'Bordado', 'Costura', 'Otros']
                     },
            "Deportes": {'color': '#C177EF',
                         'subcategories': ['Fútbol', 'Combate', 'Aventura', 'Otros']
                        },
            "Gastronomía": {'color': '#EB5369', 
                            'subcategories': ['Italiana', 'Vegetariana', 'Japonesa',  'Tailandesa',  'Mexicana',  'Hindú',  'Peruana',  'Repostería', 'Otros']
                           },
            "Idiomas": {'color': '#00AA79', 
                        'subcategories': ['Inglés', 'Portugues', 'Español', 'Italiano', 'Francés', 'Alemán', 'Otros']},
            "Música": {'color': '#FF7E60',
                       'subcategories': ['Composición', 'Producción', 'DJ', 'Otros']},
            "Infantil": {'color': '#0084B4',
                      'subcategories': ['Yoga', 'Cocina', 'Danza', 'Otros']},
            "Profesional": {'color': '#FFC971',
                            'subcategories': ['Redes Sociales', 'Marketing', 'Contabilidad', 'Oratoria', 'Locución', 'Administración', 'Ventas', 'Otros']},
            "Tecnología": {'color': '#EB9F61',
                           'subcategories': ['Desarrollo Web', 'Desarrollo Móvil', 'Modelado', 'Microsoft', 'Programación', 
                                             'Telecomunicaciones', 'Base de Datos', 'Otros']},
            "Fitness": {'color': '#222222', 
                         'subcategories': ['Yoga', 'Crossfit',' Zumba', 'Otros']},
            "Vida cotidiana":{'color': '#2981FB', 
                         'subcategories': ['Meditación', 'Otros']
            }
        }
