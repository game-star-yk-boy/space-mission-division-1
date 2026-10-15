import msvcrt
import random
import time

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
oxygen_use_per_crew_member_per_day = 3
water_use_per_crew_member_per_day = 4
water_recovery_fraction = 0.5
food_use_per_crew_member_per_day = 3
life_support_power_use_per_day = 5
mission_complete = False

# These values are made up for practice, not engineering or medical limits.
battery_capacity = 80
normal_solar = 8
shadow_days = [4, 5]
science_power = 6
science_fault_day = 5
optional_science_enabled = False
science_observations = 0
mission_aborted = False
repair_kit_available = True
repair_pending = False
emergency_delivery_used = False

# These are fictional game points, not real delivery capability.
# These are fictional emergency-help points, not real services.
emergency_delivery_cost = 10
critical_trade_battery_cost = 20
critical_trade_supply_amount = 15
delivery_pending = False
equipment_breakdown_pending = False

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

def timed_repair_input(required_word="REPAIR"):
	time_limit = 10
	deadline = time.monotonic() + time_limit
	response = ""
	last_displayed_second = None
	ignore_next_character = False
	print(f"Type {required_word} within 10 seconds to request emergency help.")

	while True:
		remaining = deadline - time.monotonic()
		if remaining <= 0:
			print("\nTime expired.")
			return None

		seconds_left = int(remaining) + 1
		if seconds_left != last_displayed_second:
			print(f"\rREPAIR ({seconds_left}s): {response:<20}", end="", flush=True)
			last_displayed_second = seconds_left

		if msvcrt.kbhit():
			character = msvcrt.getwch()
			if ignore_next_character:
				ignore_next_character = False
			elif character in ("\x00", "\xe0"):
				ignore_next_character = True
			elif character in ("\r", "\n"):
				print()
				if response.strip().upper() == required_word:
					return required_word
				print(f"Only the complete word {required_word} is accepted; no help was requested.")
				return ""
			elif character == "\b":
				response = response[:-1]
			elif character.isprintable():
				response += character
		else:
			time.sleep(0.05)

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
	if mission_day == science_fault_day:
		print("Science instrument unavailable today due to the day-5 fault.")
	print(f"Science observations collected: {science_observations}")
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
	print("Supply estimates are followed by a day-by-day battery projection.")
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
	show_power_forecast()

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

	daily_needs = calculate_daily_needs()
	projected_battery = power
	projected_science_enabled = optional_science_enabled
	solar_by_day = []
	days_with_normal_solar = 0

	for forecast_day in range(mission_day, mission_length + 1):
		today_solar = solar_generation_for_day(forecast_day)
		fault_is_unrepaired = forecast_day >= 3 and repair_kit_available
		if fault_is_unrepaired:
			today_solar = 0
		solar_by_day.append((forecast_day, today_solar))
		if today_solar == normal_solar:
			days_with_normal_solar += 1

	print(f"Essential daily power need is {daily_needs['power_needed']} points. {days_with_normal_solar} days have solar generation of {normal_solar} points. Science cost is included when the instrument is on and battery allows it.")

	for forecast_day, today_solar in solar_by_day:
		projected_battery = min(battery_capacity, projected_battery + today_solar)
		essential_power_needed = daily_needs["power_needed"]

		if projected_battery < essential_power_needed:
			print(f"Projected essential power cannot cover day {forecast_day}: have {projected_battery}, need {essential_power_needed}.")
			print("Power forecast stopped.")
			return

		projected_battery -= essential_power_needed
		estimated_battery_use = essential_power_needed
		science_included_today = False
		if projected_science_enabled:
			if forecast_day == science_fault_day:
				print("Optional science is unavailable due to the day-5 fault.")
			elif projected_battery - science_power >= critical_line:
				projected_battery -= science_power
				estimated_battery_use += science_power
				science_included_today = True
			else:
				projected_science_enabled = False
				print("Optional science would pause to preserve essential power and the critical battery reserve.")
		science_note = " [science instrument included]" if science_included_today else ""
		print(f"Day {forecast_day}: estimated battery use is {estimated_battery_use} points{science_note}; projected charge is {projected_battery}/{battery_capacity} after {today_solar} solar points.")

	print("This forecast excludes one-time repair/help costs and random science supply or battery finds.")

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
	print("T - Toggle science instrument")
	print("R - Request solar fault repair")
	print("G - Show the game guide")
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
				mission_aborted = True
				shortfall_names = ", ".join(
					supply_name.lower() for supply_name, _, _ in shortfalls
				)
				print(f"MISSION ABORTED — not enough {shortfall_names} to meet this shift's requirements.")
				print("Reserves and the mission day are unchanged.")
				print("Supplies needing attention:")
				for supply_name, reserve_amount, daily_need in shortfalls:
					print(f"{supply_name}: have {reserve_amount}, need {daily_need}.")
				print("Normal mission simulation has stopped.")
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
						delivery_pending = False
						emergency_delivery_used = True
						if equipment_breakdown_pending:
							equipment_breakdown_pending = False
							print("Delivery arrived; equipment failure repaired. It cost 10 battery points and delivered no supplies.")
					else:
						print("Emergency help remains pending; battery must stay at or above the critical line.")
				if optional_science_enabled:
					if mission_day == science_fault_day:
						print("Science instrument unavailable today due to the day-5 fault.")
					elif temporary_battery - science_power >= critical_line:
						temporary_battery -= science_power
						science_observations += 1
						print("Science instrument collected one lunar observation.")
						battery_find_roll = random.random()
						if battery_find_roll < 0.2:
							battery_points_found = 25
						elif battery_find_roll < 0.6:
							battery_points_found = 10
						else:
							battery_points_found = 0
						if battery_points_found > 0:
							battery_before_find = temporary_battery
							temporary_battery = min(battery_capacity, temporary_battery + battery_points_found)
							battery_points_added = temporary_battery - battery_before_find
							print(f"Science found {battery_points_found} battery points; {battery_points_added} added to the battery.")
						supply_find_roll = random.random()
						if supply_find_roll < 0.1:
							supplies_found = 20
						elif supply_find_roll < 0.4:
							supplies_found = 10
						elif supply_find_roll < 0.9:
							supplies_found = 5
						else:
							supplies_found = 0
						if supplies_found > 0:
							oxygen += supplies_found
							water += supplies_found
							food += supplies_found
							print(f"Science found {supplies_found} each of oxygen, water, and food.")
						else:
							print("Science found no extra oxygen, water, or food.")
					else:
						optional_science_enabled = False
						print("Science paused; battery must stay at or above the critical line.")
				power = temporary_battery
				if mission_day == science_fault_day and not emergency_delivery_used and not delivery_pending:
					breakdown_response_word = "HELP"
				elif (
					mission_day < mission_length
					and mission_day != science_fault_day
					and not emergency_delivery_used
					and not delivery_pending
					and not equipment_breakdown_pending
					and random.random() < 0.2
				):
					breakdown_response_word = "REPAIR"
				else:
					breakdown_response_word = None
				if breakdown_response_word is not None:
					equipment_breakdown_pending = True
					print("Equipment breakdown!")
					repair_response = timed_repair_input(breakdown_response_word)
					if repair_response == breakdown_response_word:
						delivery_pending = True
						print("Emergency help requested; it costs 10 battery points when it arrives after a successful shift.")
					elif repair_response is None:
						mission_aborted = True
						print("MISSION ABORTED — crew safety is the priority")
						print("Normal mission simulation has stopped.")
					else:
						print("No emergency help requested.")
				if not mission_aborted:
					critical_supplies = [
						("oxygen", oxygen),
						("water", water),
						("food", food),
					]
					for supply_name, reserve_amount in critical_supplies:
						if reserve_amount <= critical_line:
							if power - critical_trade_battery_cost >= critical_line:
								trade_choice = input(
									f"{supply_name.title()} is at the critical line. Trade 20 battery for 15 {supply_name}? (Y/N): "
								).strip().upper()
								if trade_choice == "Y":
									power -= critical_trade_battery_cost
									if supply_name == "oxygen":
										oxygen += critical_trade_supply_amount
									elif supply_name == "water":
										water += critical_trade_supply_amount
									else:
										food += critical_trade_supply_amount
									print(f"Trade complete: 15 {supply_name} added for 20 battery points.")
							else:
								print(f"Trade unavailable for {supply_name}; battery must remain at or above the critical line.")
				if unused_solar > 0:
					print(f"Unused solar due to full battery: {unused_solar}.")
				print("Final reserves:")
				print(f"Oxygen: {oxygen}")
				print(f"Water: {water}")
				print(f"Food: {food}")
				print(f"Battery: {power}/{battery_capacity}")
				if oxygen <= 0 or water <= 0 or food <= 0 or power <= 0:
					mission_aborted = True
					print("MISSION ABORTED — a required supply is depleted; crew safety is the priority.")
					print("Normal mission simulation has stopped.")
				elif mission_aborted:
					print("Normal mission simulation has stopped.")
				elif mission_day == mission_length:
					mission_complete = True
					print("MISSION SUCCESS — planned mission completed.")
				else:
					mission_day += 1
	elif menu_choice == "F":
		show_supply_forecast()
	elif menu_choice == "T":
		optional_science_enabled = not optional_science_enabled
		if optional_science_enabled:
			print("Science instrument requested.")
		else:
			print("Science instrument paused.")
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
	elif menu_choice == "G":
		print("=== Mission Console Guide ===")
		print("Goal: finish the planned mission days while keeping essential supplies available.")
		print("L: write a mission log note. S: show all saved notes from this run.")
		print("V: view current reserves and mission status.")
		print("F: compare oxygen, water, and food with daily needs to estimate supported full days, then project battery one day at a time.")
		print("The battery projection adds solar (zero on shadow days and during the unrepaired day-3 fault), subtracts essential power and requested science, and stops if essential power cannot cover a day.")
		print("Forecasts do not change real reserves or the mission day, and the battery projection excludes one-time repair and help costs and random science supply or battery finds.")
		print("A: simulate one shift. It uses supplies only when essential needs are covered.")
		print("T: switch optional science on or off. When it runs, it uses 6 battery points and collects one lunar observation; it pauses if that would cross the critical line.")
		print("The science instrument is unavailable on day 5 because of a fictional fault; it uses no power and collects nothing that day.")
		print("Each science run has a 40% chance to find 10 battery points, a 20% chance to find 25, and a 40% chance to find none. Stored battery never exceeds capacity.")
		print("It also has a separate 50% chance to find 5 each of oxygen, water, and food; a 30% chance to find 10 each; a 10% chance to find 20 each; and a 10% chance to find none.")
		print("If oxygen, water, or food reaches the critical line after a shift, you can trade 20 battery points for 15 of that supply if at least the critical battery line will remain.")
		print("R: request the day-3 solar repair; it uses the repair kit and battery after a successful shift.")
		print("A day-5 science fault prompts you to type HELP within 10 seconds. On other eligible days, a random equipment breakdown may prompt you to type REPAIR.")
		print("Emergency help costs 10 battery points when it arrives after a successful shift, adds no supplies, and resolves the breakdown.")
		print("If a CREW SAFETY ALERT appears, the shift did not run. Conserve, request help if available, or abort.")
		print("Q: safely abort the mission; later shifts will not run. X: exit the console.")
		print("All resource values are fictional classroom game points.")
	elif menu_choice == "Q":
		mission_aborted = True
		print("MISSION ABORTED — crew safety is the priority")
		print("Normal mission simulation has stopped.")
	elif menu_choice == "X":
		print("=== End of Log ===")
		break
	else:
		print("Please choose L, S, V, A, F, T, R, G, Q, or X.")