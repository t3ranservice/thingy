import time

def epoch(days):
    return days * 24 * 60 * 60 * 1000

def get_time_ranges(days_left=21):
    time_ranges = []
    week_delta = epoch(days=7)
    endTime = int(time.time() * 1000)
    while (days_left != 0):
        delta, days_to_substract = (epoch(days=days_left), days_left) if days_left < 7 else (week_delta, 7)
        startTime = endTime - delta
        time_ranges.append({'start_time': startTime/1000, 'end_time': endTime/1000})
        endTime = startTime
        days_left = days_left - days_to_substract
    return time_ranges

myvar = get_time_ranges()
for k in myvar:
    print(k['start_time'], k['end_time'])