from django import forms

FORM_CLASS = 'form-control'

class BootstrapCharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.TextInput(attrs={'class': FORM_CLASS})
        super(BootstrapCharField, self).__init__(*args, **kwargs)

class BootstrapIntegerField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.NumberInput(attrs={'class': FORM_CLASS})
        super(BootstrapIntegerField, self).__init__(*args, **kwargs)

class BootstrapDateTimeField(forms.DateTimeField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.DateTimeInput(attrs={'class': FORM_CLASS})
        super(BootstrapDateTimeField, self).__init__(*args, **kwargs)

class BootstrapEmailField(forms.EmailField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.EmailInput(attrs={'class': FORM_CLASS})
        super(BootstrapEmailField, self).__init__(*args, **kwargs)

class BootstrapRegexField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.TextInput(attrs={'class': FORM_CLASS})
        super(BootstrapRegexField, self).__init__(*args, **kwargs)
