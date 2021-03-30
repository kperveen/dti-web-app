from django import forms

from .models import Target, Indication, Model, Compound, Therapeutic


class IndicationListForm(forms.ModelForm):
    class Meta:
        model = Indication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['therapeutic'].queryset = Indication.objects.none()

        if 'therapeutic' in self.data:
            try:
                therapeutic_id = int(self.data.get('therapeutic'))
                self.fields['indication'].queryset = Indication.objects.filter(therapeutic_id=therapeutic_id).order_by()
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['indication'].queryset = self.instance.therapeutic.indication_set.order_by()