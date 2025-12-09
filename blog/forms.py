# forms.py
from django import forms
from .models import Post, Tag, Category, Comment

class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-multi-select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Post
        # Only include fields that exist in your model
        fields = ["title", "content", "category", "tags"]  # removed 'description'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "placeholder": "Write a comment...",
                "rows": 2
            })
        }
