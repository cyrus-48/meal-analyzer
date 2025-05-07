from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, FoodAnalysis, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at', 'avatar_preview')
    search_fields = ('user__username', 'location')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "No Avatar"
    avatar_preview.short_description = 'Avatar'

@admin.register(FoodAnalysis)
class FoodAnalysisAdmin(admin.ModelAdmin):
    list_display = ('title_display', 'user', 'created_at', 'is_public', 'total_likes', 'image_preview')
    list_filter = ('created_at', 'is_public', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'ingredients', 'calories', 'nutrients', 'image_preview')
    actions = ['make_public', 'make_private']

    def title_display(self, obj):
        return obj.title or 'Untitled Analysis'
    title_display.short_description = 'Title'

    def total_likes(self, obj):
        return obj.likes.count()
    total_likes.short_description = 'Likes'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = "Mark selected analyses as public"

    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = "Mark selected analyses as private"

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'is_public', 'image', 'image_preview')
        }),
        ('Analysis Results', {
            'fields': ('ingredients', 'calories', 'nutrients'),
            'classes': ('collapse',)
        }),
        ('Social', {
            'fields': ('likes',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'user', 'analysis', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'analysis__title')
    readonly_fields = ('created_at',)

    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Comment'

    fieldsets = (
        ('Comment Information', {
            'fields': ('user', 'analysis', 'text')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
