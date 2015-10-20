from activities.models import Category,SubCategory

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create categories and subcategories"

    def handle(self, *args, **options):
        self.load_categories_and_subcategories()



    def load_categories_and_subcategories(self,*args, **options):
        data = self.get_data()
        for category_name,value in data.items():
            subcategories = value['subcategories']
            category = Category.objects.create(name=category_name,color=value['color'])
            _subcategories = map(lambda x:SubCategory(name=x,category=category),\
                                 subcategories)
            SubCategory.objects.bulk_create(_subcategories)



    def get_data(self):
        return  {

            "Arte": {'color':'#46416D','subcategories':['Actuación',   'Belleza' ,   'Cinematografía' ,   'Costura' ,   'Dibujo y Pintura' , 'Diseño' ,   'Fotografía' ,   'Manualidades',   'Moda' ,   'Otros']},
            "Danza":{'color':'#38DBC7','subcategories':['Bailes de Salón' , 'Ballet' , 'Contemporáneo' , 'Exótico' , 'Folklórico' , 'Latinas' , 'Oriental' , 'Step' , 'Urbano' , 'Otros']},
            "Estilo de Vida":{'color':'#00AAD1','subcategories':['Amor y Sexo' , 'Paternidad' , 'Espiritual' , 'Habilidades', 'Manejo' , 'Mascotas' , 'Relaciones Sociales' , 'Yoga' , 'Otros']},
            "Deportes":{'color':'#C177EF','subcategories':['Boxeo', 'Fitness', 'Gimnasia', 'Golf', 'Natación', 'Tennis', 'Yoga', 'Otros']},
            "Gastronomía":{'color':'#EB5369','subcategories':['Bebidas', 'Criolla', 'Internacional', 'Degustación', 'En pareja', 'Panadería', 'Repostería' , 'Otros']},
            "Idiomas":{'color':'#00AA79','subcategories':[ 'Alemán',  'Chino',  'Español',  'Francés',  'Inglés',  'Italiano',  'Japonés',  'Lengua de señas',  'Portugués',  'Otros'  ]},
            "Música":{'color':'#FF7E60','subcategories':['Acordeón',  'Armónica',  'Audio y Producción',  'Bajo',  'Batería',  'Canto',  'DJ',  'Guitarra',  'Piano',  'Saxofón',  'Teclado',  'Teoría',  'Trompeta',  'Violín',  'Violonchelo',  'Otros']},
            "Niños":{'color':'#0084B4 ','subcategories':['Académico',  'Actuación',  'Arte',  'Bailes',  'Campamentos',  'Cocina',  'Deportes',  'Habilidades',  'Idiomas' ,   'Tecnología',  'Otros' ]},
            "Profesional":{'color':'#FFC971','subcategories':['Académico',   'Arquitectura',   'Comunicación',   'Derecho',   'Docencia',   'Entrenamiento',   'Finanzas',   'Ingeniería',   'Liderazgo',   'Management',   'Marketing',   'Recursos Humanos',   'Medicina',   'Startups',   'Otros']},
            "Tecnología":{'color':'#EB9F61','subcategories':['Animación',  'Desarrollo Web y Móvil' ,  'Diseño Web y Móvil' ,  'Juegos' ,  'Microsoft' ,  'Modelado' ,  'Programación',  'Otros']},
        }
