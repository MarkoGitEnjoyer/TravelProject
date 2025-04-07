from django.contrib import admin
from .models import Registration
from .models import Trip
from .models import Coupon
from .models import TripGalleryImage 
# Register your models here.
admin.site.register(Registration)
admin.site.register(Coupon)

# Define an inline admin descriptor for TripGalleryImage
class TripGalleryImageInline(admin.TabularInline): # Use TabularInline or StackedInline
    model = TripGalleryImage
    extra = 1 # Show 1 extra blank forms for uploading new images
    fields = ('photo', 'caption', 'alt_text') # Choose fields to show in admin inline
    # readonly_fields = ('image_preview',) # Optional: Add image preview if needed

# Define a new admin class for Trip to include the inline
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'date') # Customize as needed
    inlines = [TripGalleryImageInline] # Add the image inline here

# Unregister the default Trip admin if it was registered before
# admin.site.unregister(Trip) # Only if Trip was already registered simply

# Register Trip using the new TripAdmin class
admin.site.register(Trip,TripAdmin)
