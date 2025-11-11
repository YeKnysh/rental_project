# utils/seed.py
from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from apps.listings.models import Listing
from apps.listings.choices import ListingType
from apps.bookings.models import Booking
from apps.bookings.choices import BookingStatus
from apps.reviews.models import Review

User = get_user_model()


def _future(days: int):
    return timezone.localdate() + timedelta(days=days)


def ensure_groups_permissions():
    """Create groups and set Listing permissions: owner -> CRUD, customer -> view."""
    owner_group, _ = Group.objects.get_or_create(name="owner")
    customer_group, _ = Group.objects.get_or_create(name="customer")

    ct = ContentType.objects.get_for_model(Listing)
    perms = Permission.objects.filter(
        content_type=ct,
        codename__in=["add_listing", "change_listing", "delete_listing", "view_listing"],
    )
    owner_group.permissions.set(perms)
    customer_group.permissions.set(perms.filter(codename__in=["view_listing"]))
    return owner_group, customer_group


def ensure_user(email, *, username=None, password="Pass123!", groups=(), is_staff=False, is_superuser=False):
    base_username = (username or email.split("@")[0]).strip() or "user"
    u, _ = User.objects.get_or_create(email=email.lower().strip(), defaults={"username": base_username})
    # make sure username is set (if user existed without it)
    if not u.username:
        u.username = base_username
    if password:
        u.set_password(password)
    u.is_staff = is_staff
    u.is_superuser = is_superuser
    u.save()
    for g in groups:
        u.groups.add(g)
    return u


@transaction.atomic
def seed_min():
    """
    Minimal deterministic seed:
    - users: admin, 2 owners, 1 customer
    - listings: 3 (2 by owner1, 1 by owner2)
    - bookings: 4 statuses + 1 extra confirmed (for second review)
    - reviews: 2 (only after confirmed bookings)
    """
    owner_group, customer_group = ensure_groups_permissions()

    ensure_user("admin@example.com", password="Admin123!", is_staff=True, is_superuser=True)
    owner1 = ensure_user("owner1@example.com", password="Owner123!", groups=[owner_group])
    owner2 = ensure_user("owner2@example.com", password="Owner123!", groups=[owner_group])
    cust1 = ensure_user("customer1@example.com", password="Customer123!", groups=[customer_group])

    l1, _ = Listing.objects.get_or_create(
        owner=owner1,
        title="Sunny Studio in Cologne",
        defaults={
            "description": "Cozy studio near the center.",
            "city": "Cologne",
            "district": "Innenstadt",
            "price": 550,
            "rooms": 1,
            "listing_type": ListingType.APARTMENT,
            "is_active": True,
        },
    )
    l2, _ = Listing.objects.get_or_create(
        owner=owner1,
        title="Family Flat in Nippes",
        defaults={
            "description": "2 rooms, quiet street.",
            "city": "Cologne",
            "district": "Nippes",
            "price": 780,
            "rooms": 2,
            "listing_type": ListingType.APARTMENT,
            "is_active": True,
        },
    )
    l3, _ = Listing.objects.get_or_create(
        owner=owner2,
        title="Bonn Center Loft",
        defaults={
            "description": "Loft with high ceilings.",
            "city": "Bonn",
            "district": "Zentrum",
            "price": 990,
            "rooms": 2,
            "listing_type": getattr(ListingType, "HOUSE", ListingType.APARTMENT),
            "is_active": True,
        },
    )

    # CONFIRMED (base)
    Booking.objects.update_or_create(
        listing=l1,
        tenant=cust1,
        start_date=_future(7),
        end_date=_future(10),
        defaults={"check_in_time": time(14, 0), "status": BookingStatus.CONFIRMED},
    )
    # PENDING on the same listing but WITHOUT overlap
    Booking.objects.update_or_create(
        listing=l1,
        tenant=cust1,
        start_date=_future(12),
        end_date=_future(14),
        defaults={"check_in_time": time(15, 0), "status": BookingStatus.PENDING},
    )
    # DECLINED
    Booking.objects.update_or_create(
        listing=l2,
        tenant=cust1,
        start_date=_future(16),
        end_date=_future(18),
        defaults={"check_in_time": time(12, 0), "status": BookingStatus.DECLINED},
    )
    # CANCELLED
    Booking.objects.update_or_create(
        listing=l3,
        tenant=cust1,
        start_date=_future(20),
        end_date=_future(22),
        defaults={"check_in_time": time(14, 0), "status": BookingStatus.CANCELLED},
    )
    # EXTRA: short CONFIRMED for the 2nd review
    Booking.objects.update_or_create(
        listing=l2,
        tenant=cust1,
        start_date=_future(25),
        end_date=_future(26),
        defaults={"check_in_time": time(12, 0), "status": BookingStatus.CONFIRMED},
    )

    # Reviews (allowed thanks to confirmed bookings)
    Review.objects.update_or_create(
        listing=l1, author=cust1, defaults={"rating": 5, "comment": "Great stay, very clean!"}
    )
    Review.objects.update_or_create(
        listing=l2, author=cust1, defaults={"rating": 4, "comment": "Nice flat, would visit again."}
    )

    print(
        "Seed OK\n"
        "  Admin    : admin@example.com / Admin123!\n"
        "  Owner #1 : owner1@example.com / Owner123!\n"
        "  Owner #2 : owner2@example.com / Owner123!\n"
        "  Customer : customer1@example.com / Customer123!\n"
    )


@transaction.atomic
def unseed_min():
    """Remove the minimal seed data."""
    emails = ["admin@example.com", "owner1@example.com", "owner2@example.com", "customer1@example.com"]
    titles = ["Sunny Studio in Cologne", "Family Flat in Nippes", "Bonn Center Loft"]

    Review.objects.filter(listing__title__in=titles, author__email="customer1@example.com").delete()
    Booking.objects.filter(listing__title__in=titles, tenant__email="customer1@example.com").delete()
    Listing.objects.filter(title__in=titles).delete()
    User.objects.filter(email__in=emails).delete()
