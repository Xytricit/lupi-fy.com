# forms.py
from django import forms

from .models import Category, Comment, Post, Tag


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None, **kwargs):
        if attrs is None:
            attrs = {}
        # Remove multiple to avoid error in super
        attrs = attrs.copy()
        attrs.pop('multiple', None)
        super().__init__(attrs, **kwargs)
        # Add multiple back
        self.attrs['multiple'] = True


class PostForm(forms.ModelForm):
    description = forms.CharField(
        required=True,
        max_length=500,
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Write a short description (max 500 chars)"}
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-multi-select"}),
    )
    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={"accept": "image/*"}),
    )
    category = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter a category (e.g., #Technology)",
            }
        ),
    )

    class Meta:
        model = Post
        fields = ["title", "content", "category", "tags", "description"]

    def clean_category(self):
        value = self.cleaned_data.get("category", "") or ""
        value = value.strip()
        if not value:
            raise forms.ValidationError("Please enter a category.")
        # strip leading '#' and normalize
        name = value.lstrip("#").strip()
        if not name:
            raise forms.ValidationError("Please enter a valid category name.")
        # Resolve to Category instance
        try:
            from .models import Category
            cat, _ = Category.objects.get_or_create(name=name.title())
            return cat
        except Exception:
            raise forms.ValidationError("Could not resolve category.")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={"placeholder": "Write a comment...", "rows": 2}
            )
        }
