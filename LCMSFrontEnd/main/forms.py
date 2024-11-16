from django import forms

class SQLInputForm(forms.Form):
    sql_query = forms.CharField(widget=forms.Textarea, label="SQL Query")
