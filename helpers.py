def minutes_to_hhmm(mins):
    hours = mins//60
    minutes = mins%60
    return f'{hours:02d}:{minutes:02d}'

def minutes_to_12h(mins):
    mins%=1440
    
    hours = mins//60
    minutes = mins%60
    if hours == 0:
        h = "12"
        ampm = "AM"
    elif hours < 12:
        h = f'{hours:02d}'
        ampm = "AM"
    elif hours == 12:
        h = "12"
        ampm = "PM"
    else:
        h2 = hours-12
        h = f'{h2:02d}'
        ampm = "PM"
    
    return h + f':{minutes:02d}' + ' ' + ampm