mission_day = 1
mission_length = 14
crew_size = 4

# These are fictional classroom practice points, not engineering limits.
oxygen = 80
water = 70
food = 90
power = 60
warning_line = 50
critical_line = 25

def show_status():
	print("=== Mission Status ===")
	print(f"Mission day: {mission_day} of {mission_length}")
	print(f"Crew members: {crew_size}")
	print(f"Oxygen reserve: {oxygen}")
	print(f"Water reserve: {water}")
	print(f"Food reserve: {food}")
	print(f"Power reserve: {power}")

print("Welcome to Lunar Horizon Mission Control.")
print("This is mission day 1 of 14.")
print("The crew has four members.")

show_status()
