from django.shortcuts import render

# Create your views here.


def load(request):
    return render(request, 'tpm/load.html')