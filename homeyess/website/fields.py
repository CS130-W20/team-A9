from django import forms

FORM_CLASS = "form-control"

class BootstrapCharField(forms.CharField):
    """Form field for strings with bootstrap styling
    """
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.TextInput(attrs={"class": FORM_CLASS})
        super(BootstrapCharField, self).__init__(**kwargs)

class BootstrapIntegerField(forms.IntegerField):
    """Form field for ints with bootstrap styling
    """
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.NumberInput(attrs={"class": FORM_CLASS})
        super(BootstrapIntegerField, self).__init__(**kwargs)

class BootstrapDateTimeField(forms.DateTimeField):
    """Form field for datetimes with bootstrap styling
    """
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.DateTimeInput(attrs={"class": FORM_CLASS})
        super(BootstrapDateTimeField, self).__init__(**kwargs)

class BootstrapEmailField(forms.EmailField):
    """Form field for emails with bootstrap styling
    """
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.EmailInput(attrs={"class": FORM_CLASS})
        super(BootstrapEmailField, self).__init__(**kwargs)

class BootstrapRegexField(forms.RegexField):
    """Form field for regex with bootstrap styling
    """
    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = forms.TextInput(attrs={"class": FORM_CLASS})
        super(BootstrapRegexField, self).__init__(**kwargs)
