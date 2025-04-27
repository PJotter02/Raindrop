# This file allows us to create data structures
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

#Class to store Search history
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

# This function extract the city, state, and country from the incoming search history object
    def get_components(self):
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

    # This function takes a search history object and create a url for searching purposes
    def get_search_url(self):
        city, state, country = self.get_components()
        return reverse('weather_view') + f"?city={city}&state={state}&country={country}"

    def save(self, *args, **kwargs):
        if not self.query and all([self.city, self.state, self.country]):
            self.query = f"{self.city}, {self.state}, {self.country}"
        super().save(*args, **kwargs)

    # Handles when a user saves a location to favorites from search history
    def save_as_favorite(self, user, nickname=None):
        return FavoriteLocation.objects.create(
            user=user,
            nickname=nickname,
            city=self.city,
            state=self.state,
            country=self.country,
            coordinates=self.coordinates
        )

# Creating a class to store favorite location objects
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

    # Takes a favorite object and returns a url for searching purposes
    def get_weather_url(self):
        return reverse('weather_view') + f"?city={self.city}&state={self.state}&country={self.country}"

    def __str__(self):
        return f"{self.nickname or self.city} ({self.user.username})"
