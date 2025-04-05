from django import template

from browser.models import HydrogenaseClass

register = template.Library()


@register.simple_tag
def hydrogenase_classes():
    return HydrogenaseClass.objects.all()
