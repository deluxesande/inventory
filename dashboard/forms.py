from django import forms
from .models import *  # Import your models

class ReportsForm(forms.ModelForm):
    # Define a ModelChoiceField for categories
    category = forms.ModelChoiceField(queryset=MainCategory.objects.all(), required=False, to_field_name="name")

    # Define a ModelChoiceField for subcategories (initially empty)
    subcategory = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.save()  # Save the instance to get an 'id'

        # Set the many-to-many relationship
        if self.cleaned_data.get('category'):
            instance.category.set(self.cleaned_data['category'])

        if commit:
            instance.save()

        return instance

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Dynamically set the queryset for subcategories based on the selected category
    #     if self.instance and self.instance.category:
    #         self.fields['subcategory'].queryset = Category.objects.filter(main_category=self.instance.category)
            

    class Meta:
        model = Reports
        fields = ['description', 'receipts', 'payments']
 