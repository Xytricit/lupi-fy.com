from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser  # Assuming you have a custom user model


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        # Check for case-sensitive duplicates (NANA, nana, Nana are all different)
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email


class CaseSensitiveAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that handles case-sensitive username matching.
    """

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # Try to find the user with case-sensitive match
            try:
                # Use case-sensitive lookup (exact match)
                user = CustomUser.objects.get(username=username)
                # Verify password
                if not user.check_password(password):
                    raise forms.ValidationError("Invalid username or password.")
                # When authenticating manually, set the backend attribute so django.contrib.auth.login
                # can determine which authentication backend to use (we expect ModelBackend here).
                try:
                    user.backend = "django.contrib.auth.backends.ModelBackend"
                except Exception:
                    pass
                self.user_cache = user
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Invalid username or password.")

        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone_number", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell people about yourself..."}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email
