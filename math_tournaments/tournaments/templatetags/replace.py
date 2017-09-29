import re 

from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def replace ( string, args ): 
    search  = args.split(args[0])[1]
    replace = args.split(args[0])[2]
    return re.sub( search, replace, string ) 
