from django.shortcuts import render, redirect, reverse
from django.views import View

from .forms import UserRegisterForm


class Register(View):
    def get(self, request):
        return render(request, "registration/register.html", {"form": UserRegisterForm()})

    def post(self, request):

        form = UserRegisterForm(request.POST)

        if not form.is_valid():
            return render(request, "registration/register.html", {"form": form})

        form.save()
        return redirect(reverse("accounts:login"))
