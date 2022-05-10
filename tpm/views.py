from multiprocessing import AuthenticationError
from django.shortcuts import redirect, render
from django.views import View
from matplotlib.style import context
from tpm.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login
# Create your views here.
class Register(View):

    template_name = 'registration/register.html'
    #Q1w2@566
    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)
    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

def load(request):
    return render(request, 'tpm/load.html')


def homePage(request):
    return render(request, 'tpm/homePage.html')