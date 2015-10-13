from django import forms

class CategoryForm(forms.Form):
	category_name = forms.CharField(
		label="Category name",
		max_length=50,
		required=True,
		widget=forms.TextInput()
	)
