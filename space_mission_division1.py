# Variables for the mission status
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
shift_note = 'shift note'
continue_log = 'no'


def reserve_label(amount):
	if amount <= critical_line:
		return "RED"
	elif amount <= warning_line:
		return "AMBER"
	else:
		return "GREEN"

def show_status():
	print("=== Mission Status ===")
	print(f"Mission day: {mission_day} of {mission_length}")
	print(f"Crew members: {crew_size}")
	print(f"Oxygen reserve: {oxygen} ({reserve_label(oxygen)})")
	print(f"Water reserve: {water} ({reserve_label(water)})")
	print(f"Food reserve: {food} ({reserve_label(food)})")
	print(f"Power reserve: {power} ({reserve_label(power)})")

print("Welcome to Lunar Horizon Mission Control.")
print("This is mission day 1 of 14.")
print("The crew has four members.")

show_status()

print("=== Mission Menu ===")
print("L - Write a mission note")
menu_choice = input("Choose an option: ")
if menu_choice == "L":
	shift_note = input("Write your mission note: ")
	print("=== Mission Log ===")
	print(shift_note)
continue_log = input("type yes to continue or no to exit: ")
if continue_log.lower() == 'yes':
    print("Continuing the mission log...")
else:
    print("=== End of Log ===")