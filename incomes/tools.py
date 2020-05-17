


def sort_months(querysets):
    months = []
    for queryset in querysets:
        for ele in queryset:
            if ele['month'] not in months:
                months.append(ele['month'])
    return sorted(months)