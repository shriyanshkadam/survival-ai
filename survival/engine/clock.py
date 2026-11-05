def hour_at(start_hour, elapsed_minutes):
    return (start_hour + elapsed_minutes / 60) % 24


def phase_of_day(hour):
    if 5 <= hour < 7:
        return "dawn"
    if 7 <= hour < 17:
        return "day"
    if 17 <= hour < 20:
        return "dusk"
    return "night"

def sky_phase(hour):
    phase = phase_of_day(hour)
    if phase == "day":
        return "morning" if hour < 12 else "afternoon"
    return phase