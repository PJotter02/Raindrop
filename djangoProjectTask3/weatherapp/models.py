# models.py
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches')
    query = models.CharField(max_length=255)
    search_date = models.DateTimeField(auto_now_add=True)
    coordinates = models.CharField(max_length=50)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        ordering = ['-search_date']
        verbose_name_plural = 'Search Histories'

    def get_components(self):
        """Safer component parsing with error handling"""
        try:
            if self.city and self.state and self.country:
                return self.city, self.state, self.country

            parts = self.query.split(', ')
            return (
                parts[0].strip(),
                parts[1].strip() if len(parts) > 1 else '',
                parts[2].strip() if len(parts) > 2 else ''
            )
        except (AttributeError, IndexError):
            return '', '', ''

    def get_search_url(self):
        """URL-encoded search parameters"""
        city, state, country = self.get_components()
        return reverse('weather_view') + f"?city={city}&state={state}&country={country}"

    def save(self, *args, **kwargs):
        """Auto-populate query if components exist"""
        if not self.query and all([self.city, self.state, self.country]):
            self.query = f"{self.city}, {self.state}, {self.country}"
        super().save(*args, **kwargs)

    def save_as_favorite(self, user, nickname=None):
        """Convert search entry to favorite"""
        return FavoriteLocation.objects.create(
            user=user,
            nickname=nickname,
            city=self.city,
            state=self.state,
            country=self.country,
            coordinates=self.coordinates
        )

class FavoriteLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    nickname = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=2, validators=[MinLengthValidator(2)])
    coordinates = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['user', 'city', 'state', 'country']]

    def get_weather_url(self):
        """Generate direct weather URL using stored components"""
        return reverse('weather_view') + f"?city={self.city}&state={self.state}&country={self.country}"

    def __str__(self):
        return f"{self.nickname or self.city} ({self.user.username})"
