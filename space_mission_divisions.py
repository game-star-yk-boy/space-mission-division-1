import msvcrt
import random
import time

# Variables for the mission status
mission_day = 1
difficulty_profiles = {
	"E": {
		"difficulty": "Easy",
		"crew_size": 2,
		"mission_length": 5,
		"extra_supply_shifts": 3,
		"supply_minimum": 10,
		"medal_data": {"Bronze": 2, "Silver": 3, "Gold": 4},
	},
	"M": {
		"difficulty": "Medium",
		"crew_size": 3,
		"mission_length": 8,
		"extra_supply_shifts": 2,
		"supply_minimum": 15,
		"medal_data": {"Bronze": 3, "Silver": 4, "Gold": 5},
	},
	"H": {
		"difficulty": "Hard",
		"crew_size": 4,
		"mission_length": 10,
		"extra_supply_shifts": 1,
		"supply_minimum": 20,
		"medal_data": {"Bronze": 4, "Silver": 5, "Gold": 6},
	},
}

while True:
	difficulty_choice = input("Choose Easy, Medium, or Hard (E/M/H): ").strip().upper()
	if difficulty_choice in difficulty_profiles:
		break
	print("Please enter E, M, or H.")

selected_profile = difficulty_profiles[difficulty_choice]
difficulty = selected_profile["difficulty"]
crew_size = selected_profile["crew_size"]
mission_length = selected_profile["mission_length"]
extra_supply_shifts = selected_profile["extra_supply_shifts"]
supply_minimum = selected_profile["supply_minimum"]
medal_data = selected_profile["medal_data"]

# These are fictional classroom practice points, not engineering limits.
warning_line = 50
critical_line = 25

# These are invented practice values, not engineering standards.
oxygen_use_per_crew_member_per_day = 3
water_use_per_crew_member_per_day = 4
water_recovery_fraction = 0.5
food_use_per_crew_member_per_day = 3
starting_food_per_crew_member_per_shift = 2
life_support_power_use_per_day = 3 + crew_size
water_recovery_power_use = 1
greenhouse_enabled = False
greenhouse_grow_shifts = 0
greenhouse_water_cost = 2
greenhouse_power_cost = 2
greenhouse_harvest_after = 3
greenhouse_food_reward = 10
mission_complete = False

shifts_to_stock = mission_length + extra_supply_shifts
oxygen = oxygen_use_per_crew_member_per_day * crew_size * shifts_to_stock
gross_water_per_crew_member_per_shift = water_use_per_crew_member_per_day
net_water_per_crew_member_per_shift = gross_water_per_crew_member_per_shift * (1 - water_recovery_fraction)
water = oxygen
food = starting_food_per_crew_member_per_shift * crew_size * shifts_to_stock
power = 60

# These values are made up for practice, not engineering or medical limits.
battery_capacity = 80
normal_solar = 8
shadow_day_count = random.randint(1, min(3, mission_length - 1))
shadow_days = set(random.sample(range(1, mission_length + 1), shadow_day_count))
science_power = 6
science_fault_day = 5
optional_science_enabled = False
science_observations = 0
science_findings = []
science_finding_options = (
	"a possible water-ice signal",
	"an iron-rich mineral signature",
	"a silicate-rich regolith reading",
	"a subsurface density anomaly",
	"a localized magnetic anomaly",
)
rover_data = 0
rover_survey_power_cost = 8
mission_aborted = False
abort_reason = None
abort_day = None
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

def record_abort(reason):
	global mission_aborted, abort_reason, abort_day
	if abort_reason is None:
		abort_reason = reason
		abort_day = mission_day
	mission_aborted = True
	print(f"MISSION FAILED — {abort_reason}")

def show_final_result():
	if mission_aborted:
		print(f"MISSION FAILED — {abort_reason}")
		return

	if not mission_complete:
		return

	failure_reasons = []
	if rover_data < medal_data["Bronze"]:
		failure_reasons.append(f"rover data was {rover_data}; at least {medal_data['Bronze']} was required for Bronze")
	for supply_name, amount in (("oxygen", oxygen), ("water", water), ("food", food), ("power", power)):
		if amount <= supply_minimum:
			failure_reasons.append(f"{supply_name} was not above the required level of {supply_minimum}")

	if failure_reasons:
		print("MISSION FAILED — " + "; ".join(failure_reasons) + ".")
		return

	for medal_name in ("Gold", "Silver", "Bronze"):
		if rover_data >= medal_data[medal_name]:
			print(f"MISSION SUCCESS — {medal_name}")
			return

def show_status():
	daily_needs = calculate_daily_needs(power)
	print("=== Mission Status ===")
	print(f"Mission day: {mission_day} of {mission_length}")
	print(f"Crew members: {crew_size}")
	print(f"Oxygen reserve: {oxygen} ({reserve_label(oxygen)})")
	print(f"Water reserve: {water} ({reserve_label(water)})")
	print(f"Food reserve: {food} ({reserve_label(food)})")
	print(f"Battery charge: {power}/{battery_capacity} ({reserve_label(power)})")
	print("Recycler status uses the current battery level.")
	print(f"Water recycler: {daily_needs['recycler_status']}")
	print(f"Net water needed per shift: {daily_needs['net_water_drawn']}")
	greenhouse_status = "ON" if greenhouse_enabled else "OFF"
	print(f"Greenhouse: {greenhouse_status} ({greenhouse_grow_shifts}/{greenhouse_harvest_after} successful shifts toward harvest)")
	print(f"Solar generation today: {solar_generation_for_day(mission_day)}")
	print(f"Science requested: {'Yes' if optional_science_enabled else 'No'}")
	if mission_day == science_fault_day:
		print("Science instrument unavailable today due to the day-5 fault.")
	print(f"Science observations collected: {science_observations}")
	for finding_day, finding in science_findings:
		print(f"Science finding from day {finding_day}: {finding}.")
	print(f"Rover survey data collected: {rover_data}")
	print(f"Mission aborted: {'Yes' if mission_aborted else 'No'}")
	if mission_aborted:
		print(f"Abort reason: {abort_reason}")
		print(f"Abort day: {abort_day}")

def calculate_daily_needs(battery_charge):
	oxygen_needed = crew_size * oxygen_use_per_crew_member_per_day
	gross_water_used = crew_size * water_use_per_crew_member_per_day
	if battery_charge > warning_line:
		water_recovered = int(gross_water_used * water_recovery_fraction)
		recycler_status = "ON"
		recycler_power_needed = water_recovery_power_use
	else:
		water_recovered = 0
		recycler_status = "PAUSED"
		recycler_power_needed = 0
	net_water_drawn = gross_water_used - water_recovered
	food_needed = crew_size * food_use_per_crew_member_per_day
	power_needed = life_support_power_use_per_day + recycler_power_needed
	if greenhouse_enabled:
		net_water_drawn += greenhouse_water_cost
		power_needed += greenhouse_power_cost
	return {
		"oxygen_needed": oxygen_needed,
		"gross_water_used": gross_water_used,
		"water_recovered": water_recovered,
		"net_water_drawn": net_water_drawn,
		"food_needed": food_needed,
		"power_needed": power_needed,
		"recycler_status": recycler_status,
	}

def show_supply_forecast():
	print("=== Supply Forecast ===")
	if mission_aborted:
		print("The mission is aborted; there are no normal mission days to forecast.")
		return
	print("Supply estimates are followed by a day-by-day battery projection.")
	if mission_complete:
		mission_days_remaining = 0
		print("No mission days remain.")
	else:
		mission_days_remaining = mission_length - mission_day + 1
		print(f"Mission days remaining, including today: {mission_days_remaining}")

	daily_needs = calculate_daily_needs(power)
	print("Recycler estimate uses the current battery level.")
	print(f"Water recycler: {daily_needs['recycler_status']}; net water per shift: {daily_needs['net_water_drawn']}.")
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

	print(f"Base daily life-support power need is {life_support_power_use_per_day} points, plus {water_recovery_power_use} recycler point when projected battery is above {warning_line}. {days_with_normal_solar} days have solar generation of {normal_solar} points.")

	for forecast_day, today_solar in solar_by_day:
		projected_battery = min(battery_capacity, projected_battery + today_solar)
		daily_needs = calculate_daily_needs(projected_battery)
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
		print(f"Day {forecast_day}: recycler {daily_needs['recycler_status']}; water drawn {daily_needs['net_water_drawn']}; estimated battery use is {estimated_battery_use} points{science_note}; projected charge is {projected_battery}/{battery_capacity} after {today_solar} solar points.")

	print("This forecast excludes rover survey costs and one-time repair/help costs.")

print("Welcome to Lunar Horizon Mission Control.")
print("=== Mission Briefing ===")
print(f"Difficulty: {difficulty}")
print(f"Crew members: {crew_size}")
print(f"Planned mission shifts: {mission_length}")
print(f"Extra supply shifts: {extra_supply_shifts}")
print(f"Daily life-support power need: {life_support_power_use_per_day} points")
print(f"Scheduled solar-generation days: {mission_length - len(shadow_days)} of {mission_length} (varies each mission)")
print("Starting reserves:")
print(f"Oxygen: {oxygen}")
print(f"Water: {water}")
print(f"Food: {food}")
print(f"Battery: {power}/{battery_capacity}")

mission_log = []

while True:
	print("=== Mission Menu ===")
	print("L - Open the Mission Log")
	print("S - Show the whole Mission Log")
	print("V - View mission status")
	print("A - Simulate one life-support day")
	print("F - Forecast life-support supplies")
	print("H - Toggle greenhouse plan")
	print("O - Run robotic route survey")
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
			today_solar = solar_generation_for_day(mission_day)
			solar_fault_unrepaired = mission_day >= 3 and repair_kit_available
			if solar_fault_unrepaired:
				today_solar = 0
			battery_with_solar = power + today_solar
			temporary_battery = min(battery_capacity, battery_with_solar)
			unused_solar = max(0, battery_with_solar - battery_capacity)
			daily_needs = calculate_daily_needs(temporary_battery)
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
				shortfall_names = ", ".join(
					supply_name.lower() for supply_name, _, _ in shortfalls
				)
				reason = f"Not enough {shortfall_names} to meet this shift's requirements."
				record_abort(reason)
				print(f"CREW SAFETY EMERGENCY — {reason}")
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
				if greenhouse_enabled:
					greenhouse_grow_shifts += 1
					print(f"Greenhouse growth: {greenhouse_grow_shifts}/{greenhouse_harvest_after} successful shifts.")
					if greenhouse_grow_shifts >= greenhouse_harvest_after:
						food += greenhouse_food_reward
						greenhouse_grow_shifts = 0
						print(f"Greenhouse harvest! Added {greenhouse_food_reward} fictional food points.")
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
						finding = random.choice(science_finding_options)
						science_findings.append((mission_day, finding))
						print(f"Science finding: {finding}.")
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
						if mission_day == mission_length:
							if power - emergency_delivery_cost >= critical_line:
								power -= emergency_delivery_cost
								emergency_delivery_used = True
								equipment_breakdown_pending = False
								print("Final-shift emergency help arrived, repaired the equipment, and cost 10 battery points.")
							else:
								equipment_breakdown_pending = False
								print("Emergency help could not arrive because 10 battery points would cross the critical line; the request is closed because no shifts remain.")
						else:
							delivery_pending = True
							print("Emergency help requested; it costs 10 battery points when it arrives after a successful shift.")
					elif repair_response is None:
						record_abort(f"Timed response for {breakdown_response_word} expired.")
						print("CREW SAFETY EMERGENCY — timed response expired.")
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
					depleted_names = ", ".join(
						name for name, amount in (("oxygen", oxygen), ("water", water), ("food", food), ("power", power))
						if amount <= 0
					)
					reason = f"Required reserve depleted: {depleted_names}."
					record_abort(reason)
					print(f"CREW SAFETY EMERGENCY — {reason}")
					print("Normal mission simulation has stopped.")
				elif mission_aborted:
					print("Normal mission simulation has stopped.")
				elif mission_day == mission_length:
					mission_complete = True
					show_final_result()
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
	elif menu_choice == "H":
		greenhouse_enabled = not greenhouse_enabled
		if greenhouse_enabled:
			print("Greenhouse plan enabled; no supplies are spent by toggling it on.")
		else:
			print("Greenhouse plan disabled; no supplies are spent by toggling it off.")
	elif menu_choice == "O":
		if mission_aborted or mission_complete:
			print("Rover survey unavailable; the mission is stopped.")
		elif mission_day in shadow_days:
			print("Rover survey unavailable on a shadow day.")
		elif power - rover_survey_power_cost < critical_line:
			print("Rover survey blocked; spending 8 battery points would cross the critical line.")
		else:
			power -= rover_survey_power_cost
			print("Robotic route survey started; it cost 8 fictional battery points.")
			if random.random() < 0.7:
				rover_data += 1
				print("Rover returned useful survey data.")
			else:
				print("Rover returned without usable data.")
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
		print("The recycler uses 1 extra power point and recovers 50% of water only when battery is above the warning line; at or below it, the recycler pauses.")
		print("For 4 crew, gross water use is 4 x 4 = 16 per shift. With the recycler on, net water is 8; with it paused, water use is all 16.")
		print("Solar-generation days are randomized for each mission; the battery projection shows each day's solar points, including shadow days and the unrepaired day-3 fault.")
		print("The battery projection subtracts essential power and requested science, and stops if essential power cannot cover a day.")
		print("Forecasts do not change real reserves or the mission day, and exclude rover survey costs and one-time repair/help costs.")
		print("A: simulate one shift. It uses supplies only when essential needs are covered.")
		print("H: toggle the fictional greenhouse plan on or off. Toggling costs nothing; when on, each successful shift needs 2 extra water and 2 extra power points.")
		print("The greenhouse counter increases only after successful shifts. After 3 such shifts, it adds 10 fictional food points and resets to zero.")
		print("T: switch optional science on or off. When it runs, it uses 6 battery points and reports a randomized fictional finding; it pauses if that would cross the critical line.")
		print("The science instrument is unavailable on day 5 because of a fictional fault; it uses no power and collects nothing that day.")
		print("Science records an observation when it runs; it does not create battery or supplies because an instrument measures data rather than producing resources.")
		print("O: run a robotic route survey for 8 fictional battery points. It is unavailable on shadow days and only starts if at least the critical battery line remains.")
		print("A survey has a 70% chance to add 1 rover data; it never changes crew supplies or mission day.")
		print("If oxygen, water, or food reaches the critical line after a shift, you can trade 20 battery points for 15 of that supply if at least the critical battery line will remain.")
		print("R: request the day-3 solar repair; it uses the repair kit and battery after a successful shift.")
		print("A day-5 science fault prompts you to type HELP within 10 seconds. On other eligible days, a random equipment breakdown may prompt you to type REPAIR.")
		print("Emergency help is a separate repair-only delivery: it costs 10 battery points when it arrives after a successful shift, adds no supplies, and resolves the breakdown.")
		print("If essential reserves cannot cover a shift or a required reserve reaches zero, a crew safety emergency records the reason and stops simulation.")
		print("Q: stop the mission as operator; the reason and mission day are saved. X: exit the console.")
		print(f"Medals require finishing safely with at least {medal_data['Bronze']} rover data and oxygen, water, food, and power each above {supply_minimum}.")
		print(f"Rover data medal levels: Bronze {medal_data['Bronze']}, Silver {medal_data['Silver']}, Gold {medal_data['Gold']}; the highest earned medal is awarded.")
		print("These are invented classroom game thresholds, not real spaceflight standards.")
		print("All resource values are fictional classroom game points.")
	elif menu_choice == "Q":
		if mission_complete:
			print("The planned mission is already complete.")
		elif mission_aborted:
			print(f"Mission already stopped: {abort_reason} (day {abort_day}).")
		else:
			record_abort("Mission stopped by operator.")
			print("MISSION STOPPED BY OPERATOR — the mission ended on request.")
			print("Normal mission simulation has stopped.")
	elif menu_choice == "X":
		print("=== End of Log ===")
		break
	else:
		print("Please choose L, S, V, A, F, H, O, T, R, G, Q, or X.")
