from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate

from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(
                username=email,
                password=password,
            )
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль.")
            cleaned_data["user"] = user

        return cleaned_data
    
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone:
            return phone

        if phone.startswith("8"):
            normalized_phone = "+7" + phone[1:]
        else:
            normalized_phone = phone

        if not normalized_phone.startswith("+7") or len(normalized_phone) != 12:
            raise forms.ValidationError(
                "Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        if not normalized_phone[2:].isdigit():
            raise forms.ValidationError(
                "Телефон должен содержать только цифры после +7."
            )

        same_phone_users = User.objects.exclude(pk=self.instance.pk).filter(
            phone__in=[phone, normalized_phone, "8" + normalized_phone[2:]]
        )

        if same_phone_users.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")

        return normalized_phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "").strip()

        if not github_url:
            return github_url

        parsed_url = urlparse(github_url)
        hostname = parsed_url.netloc.lower()

        if hostname not in ("github.com", "www.github.com"):
            raise forms.ValidationError("Ссылка должна вести на GitHub.")

        return github_url