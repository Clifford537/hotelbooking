from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Room, Booking
from datetime import datetime
from django.utils.dateparse import parse_date
from decimal import Decimal

from .models import Room, Booking, Guest, BookingGuest
from django.utils import timezone
from decimal import Decimal


def home(request):
    rooms = Room.objects.filter(is_available=True)

    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    adults = request.GET.get('adults')
    children = request.GET.get('children')
    num_rooms = request.GET.get('rooms')

    # Parse dates properly
    if checkin and checkout:
        checkin_date = parse_date(checkin)
        checkout_date = parse_date(checkout)

        if checkin_date and checkout_date:
            # Exclude rooms already booked in that range
            booked_rooms = Booking.objects.filter(
                Q(start_date__lt=checkout_date),
                Q(end_date__gt=checkin_date),
                booking_status="Confirmed"
            ).values_list('room_id', flat=True)

            rooms = rooms.exclude(id__in=booked_rooms)

    # Cast numeric filters
    if adults:
        rooms = rooms.filter(capacity_adults__gte=int(adults))
    if children:
        rooms = rooms.filter(capacity_children__gte=int(children))
    if num_rooms:
        rooms = rooms.filter(total_rooms__gte=int(num_rooms)) if hasattr(Room, "total_rooms") else rooms

    context = {
        "rooms": rooms,
    }
    return render(request, "home.html", context)


def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Get params
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adults = request.GET.get("adults", 1)
    children = request.GET.get("children", 0)

    checkin_date = parse_date(checkin) if checkin else None
    checkout_date = parse_date(checkout) if checkout else None

    nights = 0
    total_price = Decimal("0.00")
    vat_amount = Decimal("0.00")
    grand_total = Decimal("0.00")

    if checkin_date and checkout_date and checkout_date > checkin_date:
        nights = (checkout_date - checkin_date).days
        total_price = room.price_per_night * nights
        vat_amount = total_price * Decimal("0.18")  # ✅ fixed here
        grand_total = total_price + vat_amount

    if request.method == "POST":
        Booking.objects.create(
            room=room,
            start_date=request.POST.get("checkin"),
            end_date=request.POST.get("checkout"),
            num_adults=adults,
            num_children=children,
            total_price=grand_total,
            booking_status="Pending",
        )
        return redirect("home")

    context = {
        "room": room,
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
        "children": children,
        "nights": nights,
        "total_price": total_price,
        "vat_amount": vat_amount,
        "grand_total": grand_total,
    }
    return render(request, "book_room.html", context)




def finalize_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        # Primary Guest
        is_primary = request.POST.get("is_primary") == "yes"
        first_name = request.POST["primary_first_name"]
        last_name = request.POST["primary_last_name"]
        email = request.POST["primary_email"]
        phone = request.POST.get("primary_phone")

        primary_guest, _ = Guest.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name, "last_name": last_name, "phone": phone}
        )

        # Booking object
        start_date = request.session.get("checkin")
        end_date = request.session.get("checkout")
        num_adults = request.session.get("num_adults")
        num_children = request.session.get("num_children")
        total_price = Decimal(str(request.session.get("total_price")))

        booking = Booking.objects.create(
            primary_guest=primary_guest,
            room=room,
            start_date=start_date,
            end_date=end_date,
            num_adults=num_adults,
            num_children=num_children,
            total_price=total_price,
            booking_status="Pending"
        )

        # Loop guests
        total_guests = int(num_adults) + int(num_children)
        for i in range(1, total_guests + 1):
            g_first = request.POST[f"guest_{i}_first_name"]
            g_last = request.POST[f"guest_{i}_last_name"]
            g_email = request.POST[f"guest_{i}_email"]
            g_phone = request.POST.get(f"guest_{i}_phone")
            is_child = request.POST[f"guest_{i}_is_child"] == "1"

            guest, _ = Guest.objects.get_or_create(
                email=g_email,
                defaults={"first_name": g_first, "last_name": g_last, "phone": g_phone}
            )

            BookingGuest.objects.create(
                booking=booking,
                guest=guest,
                is_child=is_child
            )

        return redirect("booking_success", booking_id=booking.id)

    return render(request, "booking_confirm.html", {"room": room})


    room = get_object_or_404(Room, id=room_id)

    # Get params
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adults = request.GET.get("adults", 1)
    children = request.GET.get("children", 0)

    checkin_date = parse_date(checkin) if checkin else None
    checkout_date = parse_date(checkout) if checkout else None

    nights = 0
    total_price = 0
    vat_amount = 0
    grand_total = 0

    if checkin_date and checkout_date and checkout_date > checkin_date:
        nights = (checkout_date - checkin_date).days
        total_price = room.price_per_night * nights
        vat_amount = total_price * 0.18
        grand_total = total_price + vat_amount

    if request.method == "POST":
        # Booking creation (expand with guest data later)
        Booking.objects.create(
            room=room,
            start_date=request.POST.get("checkin"),
            end_date=request.POST.get("checkout"),
            num_adults=adults,
            num_children=children,
            total_price=grand_total,
            booking_status="Pending",
        )
        return redirect("home")

    context = {
        "room": room,
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
        "children": children,
        "nights": nights,
        "total_price": total_price,
        "vat_amount": vat_amount,
        "grand_total": grand_total,
    }
    return render(request, "book_room.html", context)

    """Simple placeholder for booking page"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == "POST":
        # Example logic: create booking (expand this later)
        Booking.objects.create(
            room=room,
            start_date=request.POST.get("checkin"),
            end_date=request.POST.get("checkout"),
            booking_status="Pending",
            # Add user field if you have authentication
        )
        return redirect("home")

    return render(request, "book_room.html", {"room": room})
