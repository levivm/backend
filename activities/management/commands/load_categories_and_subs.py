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
            "Arte": {'color': '#FF5A5F',
                     'subcategories': ['Dibujo y Pintura', 'Moda', 'Fotografía', 'Diseño gráfico', 'Modelaje', 'Otros' ]},
            "Danza": {'color': '#00E2AA',
                      'subcategories': ['Ballet', 'Arabe',  'Salsa', 'Hip Hop', 'Moderna y Contemporánea', 'Bachata', 'Rumba', 
                                        'Flamenco', 'Tap', 'Social', 'Otros Urbanos', 'Otros']
                     },
            "Manualidades": {'color': '#6B10C9',
                      'subcategories': ['Joyería', 'Bisutería',  'Bordado', 'Costura', 'Otros']
                     },
            "Deporte": {'color': '#32CDDA',
                         'subcategories': ['Fútbol', 'Combate', 'Aventura', 'Otros']
                        },
            "Gastronomía": {'color': '#E5CB52',
                            'subcategories': ['Italiana', 'Vegetariana', 'Japonesa',  'Tailandesa',  'Mexicana',  'Hindú',  'Peruana',  'Repostería', 'Otros']
                           },
            "Idiomas": {'color': '#B75C8B',
                        'subcategories': ['Inglés', 'Portugues', 'Español', 'Italiano', 'Francés', 'Alemán', 'Otros']},
            "Música": {'color': '#B0CA64',
                       'subcategories': ['Composición', 'Producción', 'DJ', 'Otros']},
            "Infantil": {'color': '#D3304E',
                      'subcategories': ['Yoga', 'Cocina', 'Danza', 'Otros']},
            "Profesional": {'color': '#173770',
                            'subcategories': ['Redes Sociales', 'Marketing', 'Contabilidad', 'Oratoria', 'Locución', 'Administración', 'Ventas', 
                                              'Finanzas', 'Otros']},
            "Tecnología": {'color': '#32A3D7',
                           'subcategories': ['Desarrollo Web', 'Desarrollo Móvil', 'Modelado', 'Microsoft', 'Programación', 
                                             'Telecomunicaciones', 'Base de datos', 'Otros']},
            "Fitness": {'color': '#808CD1',
                         'subcategories': ['Yoga', 'Crossfit',' Zumba', 'Otros']},
            "Vida Cotidiana":{'color': '#2981FB',
                         'subcategories': ['Meditación', 'Otros']
            }
        }
