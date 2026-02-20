# Currently not used heavily, but ready for future time helpers.

def parse_gmt_time_str(s: str):
    # "23:00" -> (23, 0)
    parts = s.split(":")
    return int(parts[0]), int(parts[1])
