from activities.models import Category,SubCategory
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create categories and subcategories"

    def handle(self, *args, **options):
        self.load_categories_and_subcategories()



    def load_categories_and_subcategories(self,*args, **options):
        data = self.get_data()
        for category_name,subcategories in data.items():
            category = Category.objects.create(name=category_name)
            _subcategories = map(lambda x:SubCategory(name=x,category=category),\
                                 subcategories)
            SubCategory.objects.bulk_create(_subcategories)



    def get_data(self):
        return  {

            "Arte": ['Actuación',   'Belleza' ,   'Cinematografía' ,   'Costura' ,   'Dibujo y Pintura' , 'Diseño' ,   'Fotografía' ,   'Manualidades',   'Moda' ,   'Otros'],
            "Danza":['Bailes de Salón' , 'Ballet' , 'Contemporáneo' , 'Exótico' , 'Folklórico' , 'Latinas' , 'Oriental' , 'Step' , 'Urbano' , 'Otros'],
            "Estilo de Vida":['Amor y Sexo' , 'Paternidad' , 'Espiritual' , 'Habilidades', 'Manejo' , 'Mascotas' , 'Relaciones Sociales' , 'Yoga' , 'Otros'],
            "Deportes":['Boxeo', 'Fitness', 'Gimnasia', 'Golf', 'Natación', 'Tennis', 'Yoga', 'Otros'],
            "Gastronomía":['Bebidas', 'Criolla', 'Internacional', 'Degustación', 'En pareja', 'Panadería', 'Repostería' , 'Otros'],
            "Idiomas":[ 'Alemán',  'Chino',  'Español',  'Francés',  'Inglés',  'Italiano',  'Japonés',  'Lengua de señas',  'Portugués',  'Otros'  ],
            "Música":['Acordeón',  'Armónica',  'Audio y Producción',  'Bajo',  'Batería',  'Canto',  'DJ',  'Guitarra',  'Piano',  'Saxofón',  'Teclado',  'Teoría',  'Trompeta',  'Violín',  'Violonchelo',  'Otros'],
            "Niños":['Académico',  'Actuación',  'Arte',  'Bailes',  'Campamentos',  'Cocina',  'Deportes',  'Habilidades',  'Idiomas' ,   'Tecnología',  'Otros' ],
            "Profesional":['Académico',   'Arquitectura',   'Comunicación',   'Derecho',   'Docencia',   'Entrenamiento',   'Finanzas',   'Ingeniería',   'Liderazgo',   'Management',   'Marketing',   'Recursos Humanos',   'Medicina',   'Startups',   'Otros'],
            "Tecnología'":['Animación',  'Desarrollo Web y Móvil' ,  'Diseño Web y Móvil' ,  'Juegos' ,  'Microsoft' ,  'Modelado' ,  'Programación',  'Otros']



        }
