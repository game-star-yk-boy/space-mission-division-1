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

# These are invented practice values, not engineering standards.
oxygen_use_per_crew_member_per_day = 1
water_use_per_crew_member_per_day = 2
water_recovery_fraction = 0.5
food_use_per_crew_member_per_day = 1
life_support_power_use_per_day = 4
mission_complete = False

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

def calculate_daily_needs():
	oxygen_needed = crew_size * oxygen_use_per_crew_member_per_day
	gross_water_used = crew_size * water_use_per_crew_member_per_day
	water_recovered = int(gross_water_used * water_recovery_fraction)
	net_water_drawn = gross_water_used - water_recovered
	food_needed = crew_size * food_use_per_crew_member_per_day
	power_needed = life_support_power_use_per_day
	return {
		"oxygen_needed": oxygen_needed,
		"gross_water_used": gross_water_used,
		"water_recovered": water_recovered,
		"net_water_drawn": net_water_drawn,
		"food_needed": food_needed,
		"power_needed": power_needed,
	}

def show_supply_forecast():
	print("=== Supply Forecast ===")
	if mission_complete:
		mission_days_remaining = 0
		print("No mission days remain.")
	else:
		mission_days_remaining = mission_length - mission_day + 1
		print(f"Mission days remaining, including today: {mission_days_remaining}")

	daily_needs = calculate_daily_needs()
	supplies = [
		("Oxygen", oxygen, daily_needs["oxygen_needed"]),
		("Water", water, daily_needs["net_water_drawn"]),
		("Food", food, daily_needs["food_needed"]),
		("Power", power, daily_needs["power_needed"]),
	]

	for supply_name, reserve_amount, daily_need in supplies:
		if daily_need == 0:
			print(f"{supply_name}: daily need is zero; no division needed. COVERED")
			continue

		full_days_supported = reserve_amount // daily_need
		if full_days_supported >= mission_days_remaining:
			coverage = "COVERED"
		else:
			coverage = "SHORTFALL"
		print(f"{supply_name}: supports {full_days_supported} full days; {coverage}")

print("Welcome to Lunar Horizon Mission Control.")
print("This is mission day 1 of 14.")
print("The crew has four members.")

mission_log = []

while True:
	print("=== Mission Menu ===")
	print("L - Open the Mission Log")
	print("S - Show the whole Mission Log")
	print("V - View mission status")
	print("A - Simulate one life-support day")
	print("F - Forecast life-support supplies")
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
	elif menu_choice == "A":
		if mission_complete:
			print("Mission is already complete. No supplies were used.")
		else:
			daily_needs = calculate_daily_needs()
			supplies = [
				("Oxygen", oxygen, daily_needs["oxygen_needed"]),
				("Water", water, daily_needs["net_water_drawn"]),
				("Food", food, daily_needs["food_needed"]),
				("Power", power, daily_needs["power_needed"]),
			]
			shortfalls = [
				(supply_name, reserve_amount, daily_need)
				for supply_name, reserve_amount, daily_need in supplies
				if reserve_amount < daily_need
			]
			if shortfalls:
				print(f"Mission day {mission_day} was not simulated; reserves are unchanged.")
				print("Supplies needing attention:")
				for supply_name, reserve_amount, daily_need in shortfalls:
					print(f"{supply_name}: have {reserve_amount}, need {daily_need}.")
			else:
				print(f"Mission day {mission_day} simulated successfully.")
				oxygen -= daily_needs["oxygen_needed"]
				water -= daily_needs["net_water_drawn"]
				food -= daily_needs["food_needed"]
				power -= daily_needs["power_needed"]
				if mission_day == mission_length:
					mission_complete = True
					print("Mission complete!")
				else:
					mission_day += 1
	elif menu_choice == "F":
		show_supply_forecast()
	elif menu_choice == "X":
		print("=== End of Log ===")
		break
	else:
		print("Please choose L, S, V, A, F, or X.")