from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.


@ensure_csrf_cookie
def landing(request):
	return render(request,'base.html',{})


def form_modal(request):
	return render(request,'form_modal.html',{})