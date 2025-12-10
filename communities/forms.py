from django import forms
from .models import Community, CommunityPost

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'category', 'description', 'banner_image', 'community_image', 'rules']
        labels = {
            'community_image': 'Profile Picture',
            'banner_image': 'Banner Image',
            'rules': 'Community Rules',
        }

    def clean(self):
        cleaned_data = super().clean()
        banner = cleaned_data.get('banner_image')
        profile = cleaned_data.get('community_image')

        if not banner:
            self.add_error('banner_image', "A banner image is required.")
        if not profile:
            self.add_error('community_image', "A profile picture is required.")


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'image']
        labels = {
            'title': 'Post Title',
            'content': 'Content',
            'image': 'Post Image (optional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your post...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')

        if not title:
            self.add_error('title', "A title is required.")
        if not content:
            self.add_error('content', "Content cannot be empty.")
        
        # Validate image size (max 5MB)
        if image:
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                self.add_error('image', "Image size must be less than 5MB. Please crop or compress your image.")
