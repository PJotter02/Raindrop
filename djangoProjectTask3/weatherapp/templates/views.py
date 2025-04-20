from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('weather_form')  # Redirect to your weather app's home page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
