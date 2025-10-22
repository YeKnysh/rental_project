from django.contrib.auth import get_user_model
from faker import Faker
from django.contrib.auth.models import Group, Permission
import random
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from apps.listings.models import Listing
from apps.listings.choices import ListingType
from apps.bookings.models import Booking
from apps.bookings.choices import BookingStatus
from apps.reviews.models import Review
from datetime import time

fake = Faker()
User = get_user_model()


def create_users(count=30):
    for i in range(count):
        username = fake.name().replace(' ', '_').lower()   # чтобы без пробелов
        user_email = fake.unique.email()
        user_password = '12345'

        User.objects.create_user(username=username, email=user_email, password=user_password)
        print(f'User {username} created')


def create_roles():
    roles = ['owner', 'customer']
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)   # get_or_create возвращает (obj, created)
        print(f'Group {role} created')


def users_in_group():
    roles = ['owner', 'customer']
    users = User.objects.all()

    group, _ = Group.objects.get_or_create(name='owner')
    for user in users[:10]:
        user.groups.add(group)

    group, _ = Group.objects.get_or_create(name='customer')
    for user in users[10:]:
        user.groups.add(group)


# --- ниже добавил сиды и права, в том же стиле ---

def create_listings(count=20):
    owners = list(User.objects.filter(groups__name='owner'))
    if not owners:
        o, _ = User.objects.get_or_create(username='landlord_demo', defaults={'email': 'landlord_demo@example.com'})
        owners = [o]

    cities = [
        ('Cologne', 'Innenstadt'),
        ('Cologne', 'Nippes'),
        ('Bonn', 'Zentrum'),
        ('Düsseldorf', 'Altstadt'),
    ]
    types = [ListingType.APARTMENT, ListingType.HOUSE, ListingType.STUDIO]

    for _ in range(count):
        city, district = random.choice(cities)
        owner = random.choice(owners)
        Listing.objects.create(
            owner=owner,
            title=fake.sentence(nb_words=3).rstrip('.'),
            description=fake.paragraph(nb_sentences=3),
            city=city,
            district=district,
            price=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
            rooms=random.randint(1, 4),
            type=random.choice(types),
            is_active=True,
        )
    print(f'{count} listings created')


def create_bookings(count=30):
    tenants = list(User.objects.filter(groups__name='customer'))
    listings = list(Listing.objects.filter(is_active=True))
    if not tenants or not listings:
        print('No tenants or listings yet')
        return

    from datetime import time, timedelta

    created = 0
    for _ in range(count):
        tenant = random.choice(tenants)
        listing = random.choice(listings)

        # подбираем незанятый интервал дат (без пересечений с активными бронями)
        attempts = 0
        while attempts < 7:
            start = fake.date_between(start_date='-30d', end_date='+45d')
            end = fake.date_between(start_date=start, end_date=start + timedelta(days=14))
            if end < start:
                end = start

            conflict = Booking.objects.filter(listing=listing) \
                .exclude(status__in=[BookingStatus.CANCELLED, BookingStatus.DECLINED]) \
                .filter(start_date__lte=end, end_date__gte=start) \
                .exists()

            if not conflict:
                break
            attempts += 1

        if attempts == 7:
            # не нашли свободный слот — пропускаем эту попытку
            continue

        check_in = random.choice([time(12, 0), time(14, 0), time(15, 0)])
        status = random.choice([
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.DECLINED,
            BookingStatus.CANCELLED,
        ])

        Booking.objects.create(
            listing=listing,
            tenant=tenant,
            start_date=start,
            end_date=end,
            check_in_time=check_in,
            status=status,
        )
        created += 1

    print(f'{created} bookings created')



def set_basic_permissions():
    ct = ContentType.objects.get_for_model(Listing)
    perms = Permission.objects.filter(
        content_type=ct,
        codename__in=['add_listing', 'change_listing', 'delete_listing', 'view_listing'],
    )
    owner_group, _ = Group.objects.get_or_create(name='owner')
    customer_group, _ = Group.objects.get_or_create(name='customer')

    owner_group.permissions.set(perms)
    customer_group.permissions.set(perms.filter(codename__in=['view_listing']))
    print('permissions assigned: owner -> CRUD, customer -> view')

def create_reviews(count=40):
    tenants = list(User.objects.filter(groups__name='customer'))
    listings = list(Listing.objects.all())
    if not tenants or not listings:
        print('No tenants or listings yet')
        return

    for _ in range(count):
        tenant = random.choice(tenants)
        listing = random.choice(listings)
        rating = random.randint(3, 5)
        Review.objects.update_or_create(
            listing=listing,
            author=tenant,
            defaults={'rating': rating, 'comment': fake.sentence(nb_words=8)}
        )
    print(f'{count} reviews upserted')