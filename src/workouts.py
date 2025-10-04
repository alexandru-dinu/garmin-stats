import numpy as np


def to_pace_str(x: float) -> str:
    a, b = divmod(x, 1)
    b = int(60 * b)
    return f"{int(a)}:{b:02d} min/km"


start = 5 + 40 / 60  # min/km
end = 5 + 20 / 60  # min/km
laps = 37
dist = 0.4  # km

splits = np.linspace(start, end, laps)  # min/km
total_duration = np.round(np.sum((splits * dist)), 2)
diff = round((splits[0] - splits[1]) * 60, 2)

summary = f"""
start at {to_pace_str(start)}
decrease {diff} sec/lap for a total of {laps} laps (lap dist: {dist * 1000} m)
end at {to_pace_str(end)}
total duration: {total_duration} min
splits: {'\n\t'.join(to_pace_str(x) for x in splits)}
avg pace: {to_pace_str(splits.mean())}
total distance: {round(laps * dist, 2)} km
""".strip()
print(summary)
