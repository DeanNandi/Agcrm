import django_filters
from .models import Response


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Response
        fields = '__all__'
        exclude = ['Timestamp', 'Age', 'PhoneNumber', 'Qualification', 'Licence_number', 'Location', 'level_of_German',
                   'enrol_to_course',
                   'participate_in_course',
                   'time_class', 'days_class', 'questions']
