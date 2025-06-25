from django.contrib import admin
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "block", "club_head_name", "contact_number", "email")  # Show relevant details
    search_fields = ("name", "block", "club_head_name")  # Enable search

    def get_queryset(self, request):
        """ Restrict club heads to view only their own club's data """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:  # If not master user, filter to only their club
            return qs.filter(username=request.user.username)
        return qs  # Master user sees all clubs

    def get_fields(self, request, obj=None):
        """ Hide username & password from the admin panel """
        fields = ("name", "block", "club_head_name", "contact_number", "email")
        if request.user.is_superuser:  # Master user can see everything
            fields += ("username", "password")
        return fields
