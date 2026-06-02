
from django import forms
from .models import Order
from django.core.exceptions import ValidationError

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Адрес'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Комментарий'}),
        }


class FileUploadForm(forms.Form):
    """Форма для загрузки файлов с проверкой размера"""
    file = forms.FileField(
        label='Выберите файл',
        help_text='Максимальный размер файла: 1 МБ'
    )
    description = forms.CharField(
        max_length=255,
        required=False,
        label='Описание файла',
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def clean_file(self):
        file = self.cleaned_data['file']

        # Проверка размера файла (1 МБ = 1048576 байт)
        max_size = 1 * 1024 * 1024  # 1 МБ

        if file.size > max_size:
            raise ValidationError(
                f'Файл слишком большой! Максимальный размер: 1 МБ. '
                f'Ваш файл: {file.size / (1024 * 1024):.2f} МБ'
            )

        # Дополнительная проверка на тип файла (опционально)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']
        if file.content_type not in allowed_types:
            raise ValidationError(
                f'Неподдерживаемый тип файла. Разрешены: {", ".join(allowed_types)}'
            )

        return file


