from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control inp usrnm', 'placeholder': 'Username', 'autocomplete': 'off', 'autofocus': 'autofocus'}))
    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'form-control inp pswd', 'placeholder': 'Password', 'autocomplete': 'off'}))
class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    subject = forms.CharField(label='Subject', max_length=200)
    message = forms.CharField(label='Message', widget=forms.Textarea)


