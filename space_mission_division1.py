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

mission_log = []

while True:
	print("=== Mission Menu ===")
	print("L - Open the Mission Log")
	print("S - Show the whole Mission Log")
	print("V - View mission status")
	print("X - Exit the console")
	menu_choice = input("Choose an option: ").strip().upper()
	if menu_choice == "L":
		while True:
			shift_note = input("Write your mission note: ")
			mission_log.append(shift_note)
			print("=== Mission Log ===")
			print(shift_note)
			while True:
				print("=== Mission Log Options ===")
				print("L - Write another note")
				print("M - Return to the Mission Menu")
				log_choice = input("Choose a log option: ").strip().upper()
				if log_choice in ("L", "M"):
					break
				print("Please choose L or M.")
			if log_choice == "M":
				break
	elif menu_choice == "S":
		print("=== Mission Log ===")
		if mission_log:
			for note_number, note in enumerate(mission_log, start=1):
				print(f"{note_number}. {note}")
		else:
			print("No notes have been written this run.")
	elif menu_choice == "V":
		show_status()
	elif menu_choice == "X":
		print("=== End of Log ===")
		break
	else:
		print("Please choose L, S, V, or X.")