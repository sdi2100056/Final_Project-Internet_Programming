from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Φόρτωση δεδομένων Παναθηναϊκού'

    def handle(self, *args, **kwargs):
        self.stdout.write('Δημιουργία κατηγοριών...')

        # Categories
        clothes, _ = Category.objects.get_or_create(
            name='Clothes',
            defaults={'description': 'Jerseys, Hoodies, Tracksuits'}
        )

        accessory, _ = Category.objects.get_or_create(
            name='Accessories',
            defaults={'description': 'Scarves, Hats'}
        )

        equipement, _ = Category.objects.get_or_create(
            name='Εξοπλισμός',
            defaults={'description': 'Balls and Equipment'}
        )

        self.stdout.write('Product Creation')

        # Προϊόντα
        products = [
            {
                'name': 'Panathinaikos Home Jersey 2024-25',
                'category': clothes,
                'description': 'Official Home Jersey 2024-25 Season. Made from renewable fabric with the iconic logo',
                'price': 79.99,
                'stock': 50,
                'size': 'M',
                'type': 'MEN',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400'
            },
            {
                'name': 'Παναθηναϊκός Away Jersey 2024-25',
                'category': clothes,
                'description': 'Official Away Jersey with a unique design.',
                'price': 79.99,
                'stock': 40,
                'size': 'L',
                'type': 'MEN',
                'season': '2024-25',
                'color': 'White',
                'image_url': 'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400'
            },
            {
                'name': 'Παναθηναϊκός Retro Jersey 1971',
                'category': clothes,
                'description': 'The classic jersey of our team the last double season 2010.',
                'price': 69.99,
                'stock': 30,
                'size': 'M',
                'type': 'MEN',
                'season': 'RETRO',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400'
            },
            {
                'name': ' Training Shirt',
                'category': clothes,
                'description': 'Training jacket.',
                'price': 29.99,
                'stock': 100,
                'size': 'M',
                'type': 'UNISEX',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400'
            },
            {
                'name': 'Hoodie',
                'category': clothes,
                'description': 'Warm Hoodie.',
                'price': 49.99,
                'stock': 60,
                'size': 'L',
                'type': 'UNISEX',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400'
            },
            {
                'name': 'Παναθηναϊκός Track Suit',
                'category': clothes,
                'description': 'Επίσημη φόρμα προπόνησης.',
                'price': 89.99,
                'stock': 35,
                'size': 'M',
                'type': 'MEN',
                'season': '2024-25',
                'color': 'Green/Whtie',
                'image_url': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400'
            },
            {
                'name': ' Kids Jersey',
                'category': clothes,
                'description': 'Kids Jesrey.',
                'price': 39.99,
                'stock': 80,
                'size': 'S',
                'type': 'KIDS',
                'season': '2024-25',
                'color': 'Green ',
                'image_url': 'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400'
            },
            {
                'name': ' Women Jersey',
                'category': clothes,
                'description': 'Slim fit women jersey.',
                'price': 74.99,
                'stock': 45,
                'size': 'M',
                'type': 'WOMEN',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1551958219-acbc608c6377?w=400'
            },
            {
                'name': 'Παναθηναϊκός Scarf',
                'category': accessory,
                'description': 'Scarf with our team colors.',
                'price': 19.99,
                'stock': 150,
                'size': 'ONE',
                'type': 'UNISEX',
                'season': 'CLASSIC',
                'color': 'Green/White',
                'image_url': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400'
            },
            {
                'name': 'Panathinaikos Hat',
                'category': accessory,
                'description': 'Hat with the logo embroidered.',
                'price': 24.99,
                'stock': 120,
                'size': 'ONE',
                'type': 'UNISEX',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400'
            },
            {
                'name': 'Panathinaikos Beanie',
                'category': accessory,
                'description': 'Winter Beanie.',
                'price': 14.99,
                'stock': 90,
                'size': 'ONE',
                'type': 'UNISEX',
                'season': '2024-25',
                'color': 'Green',
                'image_url': 'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=400'
            },
            {
                'name': ' Football ball',
                'category': equipement,
                'description': 'Official football ball with logo.',
                'price': 34.99,
                'stock': 70,
                'size': 'ONE',
                'type': 'UNISEX',
                'season': '2024-25',
                'color': 'Green/White',
                'image_url': 'https://images.unsplash.com/photo-1614632537197-38a17061c2bd?w=400'
            },
        ]

        for product_data in products:
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )

        self.stdout.write(self.style.SUCCESS(f'✅ Δημιουργήθηκαν {Product.objects.count()} προϊόντα!'))
        self.stdout.write(self.style.SUCCESS(f'✅ Δημιουργήθηκαν {Category.objects.count()} κατηγορίες!'))