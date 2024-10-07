import datetime
from django import template

register = template.Library()

thai_months = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

@register.filter
def thai_date(value):
    if isinstance(value, datetime.date):
        day = value.day
        month = thai_months[value.month]
        year = value.year + 543  # Convert to Buddhist Era (BE)
        return f"{day} {month} {year}"
    return value
