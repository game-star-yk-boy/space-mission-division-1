# Variables for the mission status
mission_day = 1
mission_length = int(input("How many days is the mission? "))
crew_size = int(input("How many crew members? "))

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

# These values are made up for practice, not engineering or medical limits.
battery_capacity = 80
normal_solar = 8
shadow_days = [4, 5]
science_power = 6
optional_science_enabled = False
mission_aborted = False
repair_kit_available = True
repair_pending = False
emergency_delivery_used = False

# These are fictional game points, not real delivery capability.
emergency_delivery_cost = 8
emergency_delivery_supply_amount = 15
delivery_pending = False

shift_note = 'shift note'
continue_log = 'no'


def reserve_label(amount):
	if amount <= critical_line:
		return "RED"
	elif amount <= warning_line:
		return "AMBER"
	else:
		return "GREEN"

def solar_generation_for_day(day):
	if day in shadow_days:
		return 0
	return normal_solar

def show_status():
	print("=== Mission Status ===")
	print(f"Mission day: {mission_day} of {mission_length}")
	print(f"Crew members: {crew_size}")
	print(f"Oxygen reserve: {oxygen} ({reserve_label(oxygen)})")
	print(f"Water reserve: {water} ({reserve_label(water)})")
	print(f"Food reserve: {food} ({reserve_label(food)})")
	print(f"Battery charge: {power}/{battery_capacity} ({reserve_label(power)})")
	print(f"Solar generation today: {solar_generation_for_day(mission_day)}")
	print(f"Science requested: {'Yes' if optional_science_enabled else 'No'}")
	print(f"Mission aborted: {'Yes' if mission_aborted else 'No'}")

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
	print("For a day-by-day battery forecast, choose P.")
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

def show_power_forecast():
	print("=== Power Forecast ===")
	if mission_aborted:
		print("The mission is aborted; there are no normal mission days to forecast.")
		return
	if mission_complete:
		print("The mission is complete; there are no normal mission days to forecast.")
		return
	if mission_day > mission_length:
		print("There are no normal mission days left to forecast.")
		return

	print("This first forecast does not include one-time repair or delivery costs.")
	daily_needs = calculate_daily_needs()
	projected_battery = power
	projected_science_enabled = optional_science_enabled

	for forecast_day in range(mission_day, mission_length + 1):
		today_solar = solar_generation_for_day(forecast_day)
		fault_is_unrepaired = forecast_day >= 3 and repair_kit_available
		if fault_is_unrepaired:
			today_solar = 0
		projected_battery = min(battery_capacity, projected_battery + today_solar)
		essential_power_needed = daily_needs["power_needed"]
		print(f"Day {forecast_day}: solar {today_solar}; essential life-support needs {essential_power_needed}.")

		if projected_battery < essential_power_needed:
			print(f"Projected essential power cannot cover day {forecast_day}: have {projected_battery}, need {essential_power_needed}.")
			print("Power forecast stopped.")
			return

		projected_battery -= essential_power_needed
		if projected_science_enabled:
			if projected_battery - science_power >= critical_line:
				projected_battery -= science_power
				print("Optional science is included for this day.")
			else:
				projected_science_enabled = False
				print("Optional science would pause to preserve essential power and the critical battery reserve.")
		print(f"Projected battery at end of day: {projected_battery}/{battery_capacity}")

print("Welcome to Lunar Horizon Mission Control.")
print("This is mission day " + str(mission_day) + " of " + str(mission_length) + ".")
print("The crew has " + str(crew_size) + " members.")

mission_log = []

while True:
	print("=== Mission Menu ===")
	print("L - Open the Mission Log")
	print("S - Show the whole Mission Log")
	print("V - View mission status")
	print("A - Simulate one life-support day")
	print("F - Forecast life-support supplies")
	print("P - Forecast power day by day")
	print("T - Toggle science instrument")
	print("E - Request emergency supply delivery")
	print("R - Request solar fault repair")
	print("Q - Abort the mission")
	print("X - Exit the console")
	menu_choice = input("Choose an option: ").strip().upper()
	if menu_choice == "L":
		while True:
			shift_note = input("Write your mission note: ")
			mission_log.append((mission_day, shift_note))
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
			for note_number, (note_day, note) in enumerate(mission_log, start=1):
				print(f"{note_number}. Day {note_day}: {note}")
		else:
			print("No notes have been written this run.")
	elif menu_choice == "V":
		show_status()
	elif menu_choice == "A":
		if mission_aborted:
			print("Mission aborted. No further shifts can be simulated.")
		elif mission_complete:
			print("Mission is already complete. No supplies were used.")
		else:
			daily_needs = calculate_daily_needs()
			today_solar = solar_generation_for_day(mission_day)
			solar_fault_unrepaired = mission_day >= 3 and repair_kit_available
			if solar_fault_unrepaired:
				today_solar = 0
			battery_with_solar = power + today_solar
			temporary_battery = min(battery_capacity, battery_with_solar)
			unused_solar = max(0, battery_with_solar - battery_capacity)
			supplies = [
				("Oxygen", oxygen, daily_needs["oxygen_needed"]),
				("Water", water, daily_needs["net_water_drawn"]),
				("Food", food, daily_needs["food_needed"]),
				("Life-support power", temporary_battery, daily_needs["power_needed"]),
			]
			shortfalls = [
				(supply_name, reserve_amount, daily_need)
				for supply_name, reserve_amount, daily_need in supplies
				if reserve_amount < daily_need
			]
			if shortfalls:
				print("CREW SAFETY ALERT — shift not simulated")
				print("Reserves and pending tasks are unchanged.")
				print("Supplies needing attention:")
				for supply_name, reserve_amount, daily_need in shortfalls:
					print(f"{supply_name}: have {reserve_amount}, need {daily_need}.")
				print("Options: pause science to conserve power (T), request repair (R) or delivery (E) if available, or abort (Q).")
			else:
				print(f"Mission day {mission_day} simulated successfully.")
				temporary_battery -= daily_needs["power_needed"]
				oxygen -= daily_needs["oxygen_needed"]
				water -= daily_needs["net_water_drawn"]
				food -= daily_needs["food_needed"]
				if repair_pending:
					if temporary_battery - 2 >= critical_line:
						temporary_battery -= 2
						repair_kit_available = False
						repair_pending = False
						print("Solar fault repaired.")
					else:
						print("Solar repair remains pending; battery must stay at or above the critical line.")
				elif delivery_pending:
					if temporary_battery - emergency_delivery_cost >= critical_line:
						temporary_battery -= emergency_delivery_cost
						oxygen += emergency_delivery_supply_amount
						water += emergency_delivery_supply_amount
						food += emergency_delivery_supply_amount
						delivery_pending = False
						emergency_delivery_used = True
						print("Emergency delivery received: 15 oxygen, 15 water, and 15 food.")
					else:
						print("Emergency delivery remains pending; battery must stay at or above the critical line.")
				if optional_science_enabled:
					if temporary_battery - science_power >= critical_line:
						temporary_battery -= science_power
						print("Science instrument operated.")
					else:
						optional_science_enabled = False
						print("Science paused; battery must stay at or above the critical line.")
				power = temporary_battery
				if unused_solar > 0:
					print(f"Unused solar due to full battery: {unused_solar}.")
				print("Final reserves:")
				print(f"Oxygen: {oxygen}")
				print(f"Water: {water}")
				print(f"Food: {food}")
				print(f"Battery: {power}/{battery_capacity}")
				if mission_day == mission_length:
					mission_complete = True
					print("MISSION SUCCESS — planned mission completed.")
				else:
					mission_day += 1
	elif menu_choice == "F":
		show_supply_forecast()
	elif menu_choice == "P":
		show_power_forecast()
	elif menu_choice == "T":
		optional_science_enabled = not optional_science_enabled
		if optional_science_enabled:
			print("Science instrument requested.")
		else:
			print("Science instrument paused.")
	elif menu_choice == "E":
		if emergency_delivery_used or delivery_pending:
			print("Emergency delivery is unavailable; it has already been used or requested.")
		elif power < emergency_delivery_cost:
			print("Emergency delivery is unavailable; not enough battery points.")
		else:
			power -= emergency_delivery_cost
			delivery_pending = True
			print("Emergency delivery requested; supplies will arrive after a successful shift.")
	elif menu_choice == "R":
		if mission_day < 3:
			print("No solar fault has happened yet; repair is unavailable until day 3.")
		elif not repair_kit_available:
			print("Solar fault is already repaired; repair is unavailable.")
		elif repair_pending:
			print("Solar repair is already pending.")
		else:
			repair_pending = True
			print("Solar repair requested; it will be attempted after a successful shift.")
	elif menu_choice == "Q":
		mission_aborted = True
		print("MISSION ABORTED — crew safety is the priority")
		print("Normal mission simulation has stopped.")
	elif menu_choice == "X":
		print("=== End of Log ===")
		break
	else:
		print("Please choose L, S, V, A, F, P, T, E, R, Q, or X.")