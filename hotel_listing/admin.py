from django.contrib import admin
from .models import Room, Guest, Booking, BookingGuest, Meal, MealPreference, Payment


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "bed_type", "capacity_adults",
                    "capacity_children", "price_per_night", "is_available")
    list_filter = ("room_type", "bed_type", "is_available")
    search_fields = ("room_number", "room_type", "bed_type")
    ordering = ("room_number",)


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name", "email", "phone")
    ordering = ("last_name", "first_name")


class BookingGuestInline(admin.TabularInline):
    model = BookingGuest
    extra = 1


class MealPreferenceInline(admin.TabularInline):
    model = MealPreference
    extra = 1
    autocomplete_fields = ['meal']  # Optional: makes meal selection easier


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "primary_guest", "room", "start_date",
                    "end_date", "num_adults", "num_children",
                    "total_price", "booking_status", "created_at")
    list_filter = ("booking_status", "start_date", "end_date", "created_at")
    search_fields = ("id", "primary_guest__first_name", "primary_guest__last_name", "room__room_number")
    ordering = ("-created_at",)
    inlines = [BookingGuestInline, MealPreferenceInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "amount", "payment_method", "payment_status", "payment_date", "transaction_id")
    list_filter = ("payment_method", "payment_status", "payment_date")
    search_fields = ("transaction_id", "booking__id", "booking__primary_guest__first_name", "booking__primary_guest__last_name")
    ordering = ("-payment_date",)


@admin.register(BookingGuest)
class BookingGuestAdmin(admin.ModelAdmin):
    list_display = ("booking", "guest", "is_child")
    list_filter = ("is_child",)
    search_fields = ("booking__id", "guest__first_name", "guest__last_name")


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(MealPreference)
class MealPreferenceAdmin(admin.ModelAdmin):
    list_display = ("booking", "get_meal_name", "selected")
    list_filter = ("selected", "meal")
    search_fields = ("booking__id", "booking__primary_guest__first_name", "meal__name")

    def get_meal_name(self, obj):
        return obj.meal.name
    get_meal_name.short_description = "Meal"
