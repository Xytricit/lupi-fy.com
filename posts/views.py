from django.shortcuts import render

def index(request):
    return render(request, 'posts/index.html')  # points to posts/templates/posts/index.html
