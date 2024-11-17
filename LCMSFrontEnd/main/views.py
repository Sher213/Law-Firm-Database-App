from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db import connection
from .forms import SQLInputForm

def home(request):
    return render(request, 'main/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def execute_sql(request):
    result = None
    if request.method == 'POST':
        form = SQLInputForm(request.POST)
        if form.is_valid():
            sql_query = form.cleaned_data['sql_query']
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    result = cursor.fetchall() if cursor.description else "Query executed successfully."
            except Exception as e:
                result = f"Error: {str(e)}"
    else:
        form = SQLInputForm()
    return render(request, 'main/execute_sql.html', {'form': form, 'result': result})

def contact(request):
    return render(request, 'main/contact.html')

