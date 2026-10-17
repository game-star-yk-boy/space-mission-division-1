import random
import time
import streamlit as st

st.set_page_config(
	page_title="Lunar Horizon Mission Control",
	layout="wide",
	initial_sidebar_state="expanded",
)

# A colorful control-room theme: dark space, bright planets, and readable panels.
st.markdown("""
<style>
.stApp {
    background: radial-gradient(ellipse at top, #263b70 0%, #111a35 48%, #090d1c 100%);
    color: #f5f7ff;
}
[data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #18264b 0%, #10182f 100%);
    border-right: 2px solid #40d9ff;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(46, 73, 125, .95), rgba(31, 44, 83, .95));
    border: 1px solid #5b83d6;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, .22);
}
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] {
    background: #202f59;
    border-radius: 10px 10px 0 0;
    padding: 8px 14px;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #40d9ff;
    color: #10182f;
}
.stButton > button, [data-testid="stFormSubmitButton"] button {
    background: linear-gradient(90deg, #6049d8, #a34bd1);
    color: white;
    border: 1px solid #c7a5ff;
    border-radius: 11px;
    font-weight: 700;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(90deg, #138dbb, #21b9a8);
    border-color: #7df5e5;
    color: white;
}
[data-testid="stExpander"] {
    background: rgba(31, 47, 88, .75);
    border: 1px solid #526eaf;
    border-radius: 12px;
}
h1, h2, h3 { color: #8be9ff !important; }
</style>
""", unsafe_allow_html=True)

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

if "mission_started" not in st.session_state:
	st.session_state["mission_started"] = False

if not st.session_state["mission_started"]:
	st.title("🌙🚀 Lunar Horizon Mission Control")
	st.write("✨ Before the mission appears, choose your difficulty level.")
	chosen_difficulty = st.selectbox(
		"🎚️ How challenging should your mission be?",
		("Choose a difficulty...", "🟢 Easy", "🟡 Medium", "🔴 Hard"),
		key="setup_difficulty",
	)
	if chosen_difficulty != "Choose a difficulty...":
		difficulty_codes = {"🟢 Easy": "E", "🟡 Medium": "M", "🔴 Hard": "H"}
		st.session_state["difficulty_choice"] = difficulty_codes[chosen_difficulty]
		st.session_state["mission_started"] = True
		st.session_state["mission_difficulty_choice"] = None
		st.rerun()
	st.stop()

difficulty_choice = st.session_state["difficulty_choice"]
st.title("🌙🚀 Lunar Horizon Mission Control")
st.caption("🛰️ Mission in progress — every choice counts!")

selected_profile = difficulty_profiles[difficulty_choice]
difficulty = selected_profile["difficulty"]
crew_size = selected_profile["crew_size"]
mission_length = selected_profile["mission_length"]
extra_supply_shifts = selected_profile["extra_supply_shifts"]
supply_minimum = selected_profile["supply_minimum"]
medal_data = selected_profile["medal_data"]

# These are fictional classroom practice values, not real-world limits.
warning_line = 50
critical_line = 25
oxygen_use_per_crew_member_per_day = 3
water_use_per_crew_member_per_day = 4
water_recovery_fraction = 0.5
food_use_per_crew_member_per_day = 3
starting_food_per_crew_member_per_shift = 2
life_support_power_use_per_day = 3 + crew_size
water_recovery_power_use = 1
greenhouse_water_cost = 2
greenhouse_power_cost = 2
greenhouse_harvest_after = 3
greenhouse_food_reward = 10
battery_capacity = 80
normal_solar = 8
science_power = 6
science_fault_day = 5
science_finding_options = (
	"a possible water-ice signal",
	"an iron-rich mineral signature",
	"a silicate-rich regolith reading",
	"a subsurface density anomaly",
	"a localized magnetic anomaly",
)
rover_survey_power_cost = 8
emergency_delivery_cost = 10
critical_trade_battery_cost = 20
critical_trade_supply_amount = 15

if st.session_state.get("mission_difficulty_choice") != difficulty_choice:
	shifts_to_stock = mission_length + extra_supply_shifts
	initial_oxygen = oxygen_use_per_crew_member_per_day * crew_size * shifts_to_stock
	shadow_day_count = random.randint(1, min(3, mission_length - 1))
	st.session_state.update({
		"mission_difficulty_choice": difficulty_choice,
		"mission_day": 1,
		"mission_complete": False,
		"mission_aborted": False,
		"abort_reason": None,
		"abort_day": None,
		"oxygen": initial_oxygen,
		"water": initial_oxygen,
		"food": starting_food_per_crew_member_per_shift * crew_size * shifts_to_stock,
		"power": 60,
		"shadow_days": set(random.sample(range(1, mission_length + 1), shadow_day_count)),
		"greenhouse_enabled": False,
		"greenhouse_grow_shifts": 0,
		"optional_science_enabled": False,
		"science_observations": 0,
		"science_findings": [],
		"rover_data": 0,
		"repair_kit_available": True,
		"repair_pending": False,
		"emergency_delivery_used": False,
		"delivery_pending": False,
		"equipment_breakdown_pending": False,
		"mission_log": [],
		"mission_history": [],
		"current_shift_record": None,
		"pending_response_word": None,
		"pending_response_deadline": None,
		"console_exited": False,
	})

mission_day = st.session_state["mission_day"]
mission_complete = st.session_state["mission_complete"]
mission_aborted = st.session_state["mission_aborted"]
abort_reason = st.session_state["abort_reason"]
abort_day = st.session_state["abort_day"]
oxygen = st.session_state["oxygen"]
water = st.session_state["water"]
food = st.session_state["food"]
power = st.session_state["power"]
shadow_days = st.session_state["shadow_days"]
greenhouse_enabled = st.session_state["greenhouse_enabled"]
greenhouse_grow_shifts = st.session_state["greenhouse_grow_shifts"]
optional_science_enabled = st.session_state["optional_science_enabled"]
science_observations = st.session_state["science_observations"]
science_findings = st.session_state["science_findings"]
rover_data = st.session_state["rover_data"]
repair_kit_available = st.session_state["repair_kit_available"]
repair_pending = st.session_state["repair_pending"]
emergency_delivery_used = st.session_state["emergency_delivery_used"]
delivery_pending = st.session_state["delivery_pending"]
equipment_breakdown_pending = st.session_state["equipment_breakdown_pending"]
mission_log = st.session_state["mission_log"]
mission_history = st.session_state["mission_history"]
current_shift_record = st.session_state["current_shift_record"]
pending_response_word = st.session_state["pending_response_word"]
pending_response_deadline = st.session_state["pending_response_deadline"]


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

def record_abort(reason):
	global mission_aborted, abort_reason, abort_day
	if st.session_state["abort_reason"] is None:
		st.session_state["abort_reason"] = reason
		st.session_state["abort_day"] = st.session_state["mission_day"]
	st.session_state["mission_aborted"] = True
	mission_aborted = st.session_state["mission_aborted"]
	abort_reason = st.session_state["abort_reason"]
	abort_day = st.session_state["abort_day"]

def reserve_snapshot():
	return {
		"Oxygen": oxygen,
		"Water": water,
		"Food": food,
		"Battery": power,
	}

def record_resource_change(resource, amount, reason):
	if current_shift_record is not None and amount != 0:
		current_shift_record["changes"].append({
			"resource": resource,
			"amount": amount,
			"reason": reason,
		})

def save_history_record(record, note=None):
	if note:
		record["notes"].append(note)
	record["ending_reserves"] = reserve_snapshot()
	mission_history.append(record)
	st.session_state["mission_history"] = mission_history

def record_resource_action(day, event, starting_reserves, resource, amount, reason, note):
	save_history_record({
		"day": day,
		"event": event,
		"changes": [{"resource": resource, "amount": amount, "reason": reason}],
		"notes": [],
		"starting_reserves": starting_reserves,
	}, note)

def finish_current_shift_history(note=None):
	global current_shift_record
	if current_shift_record is not None:
		save_history_record(current_shift_record, note)
		current_shift_record = None
		st.session_state["current_shift_record"] = None

def show_final_result():
	if mission_aborted:
		return f"MISSION FAILED — {abort_reason}"

	if not mission_complete:
		return None

	failure_reasons = []
	if rover_data < medal_data["Bronze"]:
		failure_reasons.append(f"rover data was {rover_data}; at least {medal_data['Bronze']} was required for Bronze")
	for supply_name, amount in (("oxygen", oxygen), ("water", water), ("food", food), ("power", power)):
		if amount <= supply_minimum:
			failure_reasons.append(f"{supply_name} was not above the required level of {supply_minimum}")

	if failure_reasons:
		return "MISSION FAILED — " + "; ".join(failure_reasons) + "."

	for medal_name in ("Gold", "Silver", "Bronze"):
		if rover_data >= medal_data[medal_name]:
			return f"MISSION SUCCESS — {medal_name}"
	return "MISSION FAILED — rover data did not reach Bronze."

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

def save_game_state():
	for state_name in (
		"mission_day", "mission_complete", "mission_aborted", "abort_reason", "abort_day",
		"oxygen", "water", "food", "power", "shadow_days", "greenhouse_enabled",
		"greenhouse_grow_shifts", "optional_science_enabled", "science_observations",
		"science_findings", "rover_data", "repair_kit_available", "repair_pending",
		"emergency_delivery_used", "delivery_pending", "equipment_breakdown_pending",
		"mission_log", "mission_history", "current_shift_record",
		"pending_response_word", "pending_response_deadline",
	):
		st.session_state[state_name] = globals()[state_name]

def finish_shift(trade_choices):
	global mission_day, mission_complete
	for supply_name, amount in (("oxygen", oxygen), ("water", water), ("food", food)):
		if amount <= critical_line and trade_choices[supply_name] == "Trade":
			if power - critical_trade_battery_cost >= critical_line:
				globals()[supply_name] += critical_trade_supply_amount
				globals()["power"] -= critical_trade_battery_cost
				record_resource_change(supply_name.title(), critical_trade_supply_amount, "Supply trade")
				record_resource_change("Battery", -critical_trade_battery_cost, "Supply trade")
				st.success(f"Trade complete: added 15 {supply_name} for 20 battery points.")
			else:
				st.warning(f"Trade unavailable for {supply_name}; battery must stay at or above the critical line.")

	depleted_supplies = [
		name for name, amount in (("oxygen", oxygen), ("water", water), ("food", food), ("power", power))
		if amount <= 0
	]
	if depleted_supplies:
		record_abort(f"Required reserve depleted: {', '.join(depleted_supplies)}.")
	elif mission_aborted:
		pass
	elif mission_day == mission_length:
		mission_complete = True
		st.session_state["mission_complete"] = True
	else:
		mission_day += 1
	finish_current_shift_history()
	save_game_state()

def simulate_shift(trade_choices):
	global mission_day, mission_complete, oxygen, water, food, power
	global greenhouse_grow_shifts, repair_kit_available, repair_pending
	global delivery_pending, emergency_delivery_used, equipment_breakdown_pending
	global optional_science_enabled, science_observations, science_findings
	global mission_aborted, abort_reason, abort_day, pending_response_word, pending_response_deadline
	global current_shift_record

	if mission_aborted or mission_complete:
		st.info("The mission is stopped; no shift was simulated.")
		return

	today_solar = solar_generation_for_day(mission_day)
	if mission_day >= 3 and repair_kit_available:
		today_solar = 0
	temporary_battery = min(battery_capacity, power + today_solar)
	daily_needs = calculate_daily_needs(temporary_battery)
	supplies = (
		("oxygen", oxygen, daily_needs["oxygen_needed"]),
		("water", water, daily_needs["net_water_drawn"]),
		("food", food, daily_needs["food_needed"]),
		("battery", temporary_battery, daily_needs["power_needed"]),
	)
	shortfalls = [name for name, amount, need in supplies if amount < need]
	if shortfalls:
		record_abort(f"Not enough {', '.join(shortfalls)} to meet this shift's requirements.")
		st.error(f"Shift stopped: not enough {', '.join(shortfalls)}.")
		save_history_record({
			"day": mission_day,
			"event": "Shift attempt",
			"changes": [],
			"notes": [f"Shift not completed because of a shortfall in {', '.join(shortfalls)}. Supplies were unchanged."],
			"starting_reserves": reserve_snapshot(),
		})
		save_game_state()
		return

	current_shift_record = {
		"day": mission_day,
		"event": "Life-support shift",
		"changes": [],
		"notes": [],
		"starting_reserves": reserve_snapshot(),
	}
	st.session_state["current_shift_record"] = current_shift_record
	st.success(f"Mission day {mission_day} simulated successfully.")
	solar_added = temporary_battery - power
	record_resource_change("Battery", solar_added, "Solar charging")
	temporary_battery -= daily_needs["power_needed"]
	record_resource_change("Battery", -life_support_power_use_per_day, "Life support power")
	if daily_needs["recycler_status"] == "ON":
		record_resource_change("Battery", -water_recovery_power_use, "Water recycler power")
	if greenhouse_enabled:
		record_resource_change("Battery", -greenhouse_power_cost, "Greenhouse power")
	oxygen -= daily_needs["oxygen_needed"]
	record_resource_change("Oxygen", -daily_needs["oxygen_needed"], "Crew use")
	water -= daily_needs["gross_water_used"]
	record_resource_change("Water", -daily_needs["gross_water_used"], "Crew use")
	water += daily_needs["water_recovered"]
	record_resource_change("Water", daily_needs["water_recovered"], "Water recycler recovery")
	if greenhouse_enabled:
		water -= greenhouse_water_cost
		record_resource_change("Water", -greenhouse_water_cost, "Greenhouse use")
	food -= daily_needs["food_needed"]
	record_resource_change("Food", -daily_needs["food_needed"], "Crew use")
	if greenhouse_enabled:
		greenhouse_grow_shifts += 1
		if greenhouse_grow_shifts >= greenhouse_harvest_after:
			food += greenhouse_food_reward
			record_resource_change("Food", greenhouse_food_reward, "Greenhouse harvest")
			greenhouse_grow_shifts = 0
			st.success(f"Greenhouse harvest added {greenhouse_food_reward} food points.")

	if repair_pending:
		if temporary_battery - 2 >= critical_line:
			temporary_battery -= 2
			record_resource_change("Battery", -2, "Solar repair")
			repair_kit_available = False
			repair_pending = False
			st.success("Solar fault repaired.")
		else:
			st.warning("Solar repair remains pending; battery must stay at or above the critical line.")
	elif delivery_pending:
		if temporary_battery - emergency_delivery_cost >= critical_line:
			temporary_battery -= emergency_delivery_cost
			record_resource_change("Battery", -emergency_delivery_cost, "Emergency support")
			delivery_pending = False
			emergency_delivery_used = True
			if equipment_breakdown_pending:
				equipment_breakdown_pending = False
			st.success("Emergency help arrived, repaired equipment, and delivered no supplies.")
		else:
			st.warning("Emergency help remains pending; battery must stay at or above the critical line.")

	if optional_science_enabled:
		if mission_day == science_fault_day:
			st.warning("Science instrument unavailable today due to the day-5 fault.")
		elif temporary_battery - science_power >= critical_line:
			temporary_battery -= science_power
			record_resource_change("Battery", -science_power, "Science instrument")
			science_observations += 1
			finding = random.choice(science_finding_options)
			science_findings.append((mission_day, finding))
			st.success(f"Science finding: {finding}.")
		else:
			optional_science_enabled = False
			st.warning("Science paused to keep the battery at or above the critical line.")

	power = temporary_battery
	if mission_day == science_fault_day and not emergency_delivery_used and not delivery_pending:
		pending_response_word = "HELP"
	elif (
		mission_day < mission_length
		and mission_day != science_fault_day
		and not emergency_delivery_used
		and not delivery_pending
		and not equipment_breakdown_pending
		and random.random() < 0.2
	):
		pending_response_word = "REPAIR"

	if pending_response_word:
		equipment_breakdown_pending = True
		pending_response_deadline = time.monotonic() + 10
		st.session_state["emergency_response_text"] = ""
		st.warning(f"Equipment breakdown! Type {pending_response_word} within 10 seconds to request help.")
		save_game_state()
		return

	finish_shift(trade_choices)

def handle_emergency_response(response, trade_choices):
	global pending_response_word, pending_response_deadline, power
	global delivery_pending, emergency_delivery_used, equipment_breakdown_pending
	if time.monotonic() > pending_response_deadline:
		record_abort(f"Timed response for {pending_response_word} expired.")
		st.error("Time expired. The mission has stopped.")
		finish_current_shift_history(f"Shift ended because the {pending_response_word} response timer expired.")
	else:
		if response.strip().upper() == pending_response_word:
			if mission_day == mission_length:
				if power - emergency_delivery_cost >= critical_line:
					power -= emergency_delivery_cost
					record_resource_change("Battery", -emergency_delivery_cost, "Final-shift emergency support")
					emergency_delivery_used = True
					equipment_breakdown_pending = False
					st.success("Final-shift emergency help arrived and repaired the equipment.")
				else:
					equipment_breakdown_pending = False
					st.warning("Help could not arrive without crossing the critical battery line; no shifts remain.")
			else:
				delivery_pending = True
				if current_shift_record is not None:
					current_shift_record["notes"].append("Emergency support was requested; its battery cost is recorded on the next shift.")
				st.success("Emergency help requested. It will cost 10 battery points after a successful shift.")
		else:
			st.info(f"The exact word {pending_response_word} was not entered. No help was requested.")
			if current_shift_record is not None:
				current_shift_record["notes"].append("The emergency response word was incorrect; no help was requested.")
	pending_response_word = None
	pending_response_deadline = None
	if not mission_aborted:
		finish_shift(trade_choices)
	else:
		save_game_state()

def build_power_forecast():
	projected_battery = power
	projected_science = optional_science_enabled
	forecast = []
	for forecast_day in range(mission_day, mission_length + 1):
		today_solar = solar_generation_for_day(forecast_day)
		if forecast_day >= 3 and repair_kit_available:
			today_solar = 0
		projected_battery = min(battery_capacity, projected_battery + today_solar)
		daily_needs = calculate_daily_needs(projected_battery)
		if projected_battery < daily_needs["power_needed"]:
			forecast.append({"day": forecast_day, "solar": today_solar, "stopped": True})
			break
		projected_battery -= daily_needs["power_needed"]
		science_included = False
		if projected_science and forecast_day != science_fault_day:
			if projected_battery - science_power >= critical_line:
				projected_battery -= science_power
				science_included = True
			else:
				projected_science = False
		forecast.append({
			"day": forecast_day,
			"solar": today_solar,
			"recycler": daily_needs["recycler_status"],
			"water": daily_needs["net_water_drawn"],
			"battery": projected_battery,
			"science": science_included,
			"stopped": False,
		})
	return forecast

if st.session_state["console_exited"]:
	st.info("Mission console exited.")
	st.stop()

pending_response = st.session_state["pending_response_word"] is not None
trade_choices = {}

with st.sidebar:
	st.divider()
	st.header("🎮 Mission Actions")
	with st.expander("🔄 Space trade choices"):
		st.caption("Choose what to trade only if a reserve reaches the critical line after a shift.")
		for supply_name in ("oxygen", "water", "food"):
			trade_choices[supply_name] = st.selectbox(
				f"🔋 Trade battery for {supply_name}?",
				("No trade", "Trade"),
				key=f"trade_{supply_name}",
				disabled=pending_response,
			)

	if st.button("📅 Simulate one shift", disabled=pending_response, use_container_width=True):
		simulate_shift(trade_choices)
	show_forecast = st.button("🔭 Forecast supplies", disabled=pending_response, use_container_width=True)
	if st.button("🌱 Toggle greenhouse", disabled=pending_response, use_container_width=True):
		greenhouse_enabled = not greenhouse_enabled
		st.session_state["greenhouse_enabled"] = greenhouse_enabled
	if st.button("🤖 Run rover survey", disabled=pending_response, use_container_width=True):
		if mission_aborted or mission_complete:
			st.info("Rover survey unavailable; the mission is stopped.")
		elif mission_day in shadow_days:
			st.warning("Rover survey unavailable on a shadow day.")
		elif power - rover_survey_power_cost < critical_line:
			st.warning("Rover survey blocked; spending 8 battery points would cross the critical line.")
		else:
			reserves_before_survey = reserve_snapshot()
			power -= rover_survey_power_cost
			if random.random() < 0.7:
				rover_data += 1
				st.success("Rover returned useful survey data.")
				outcome_note = "Rover returned useful survey data."
			else:
				st.info("Rover returned without usable data.")
				outcome_note = "Rover returned without usable data."
			record_resource_action(
				mission_day,
				"Rover survey",
				reserves_before_survey,
				"Battery",
				-rover_survey_power_cost,
				"Rover survey power",
				outcome_note,
			)
			save_game_state()
	if st.button("🧪 Toggle science", disabled=pending_response, use_container_width=True):
		optional_science_enabled = not optional_science_enabled
		st.session_state["optional_science_enabled"] = optional_science_enabled
	if st.button("🛠️ Request solar repair", disabled=pending_response, use_container_width=True):
		if mission_day < 3:
			st.info("No solar fault has happened yet; repair is available from day 3.")
		elif not repair_kit_available:
			st.info("Solar fault is already repaired.")
		elif repair_pending:
			st.info("Solar repair is already pending.")
		else:
			repair_pending = True
			st.session_state["repair_pending"] = repair_pending
			st.success("Solar repair requested; it will be attempted after a successful shift.")
	show_status = st.button("📊 View mission status", disabled=pending_response, use_container_width=True)
	show_guide = st.button("📖 Show game guide", disabled=pending_response, use_container_width=True)
	if st.button("🛑 Abort mission", disabled=pending_response, use_container_width=True):
		record_abort("Mission stopped by operator.")
	if st.button("🚪 Exit console", disabled=pending_response, use_container_width=True):
		st.session_state["console_exited"] = True
		st.rerun()

	if st.session_state["pending_response_word"] is not None:
		response_word = st.session_state["pending_response_word"]
		st.warning("Emergency response required")
		with st.form("emergency_response_form"):
			response_text = st.text_input(
				f"Type {response_word} to request emergency help",
				key=f"emergency_response_text_{mission_day}_{response_word}",
			)
			response_submitted = st.form_submit_button("📡 Send emergency response")
		if response_submitted:
			handle_emergency_response(response_text, trade_choices)

briefing_tab, data_tab, systems_tab, log_tab, history_tab = st.tabs(
	("📋 Mission Briefing", "📊 Mission Data", "⚙️ Mission Systems", "📝 Mission Log", "📚 Mission History")
)

with briefing_tab:
	st.subheader("📋 Mission Briefing")
	st.write(f"🎚️ Difficulty: {difficulty}")
	st.write(f"📅 Mission day: {mission_day} of {mission_length}")
	st.write(f"👩‍🚀 Crew members: {crew_size}")
	st.write(f"📦 Extra supply shifts: {extra_supply_shifts}")
	st.write(f"☀️ Scheduled solar-generation days: {mission_length - len(shadow_days)} of {mission_length}")
	st.write(f"🚦 Mission status: {'Aborted' if mission_aborted else 'Complete' if mission_complete else 'In progress'}")
	if mission_complete or mission_aborted:
		st.subheader("🏁 Mission Result")
		result = show_final_result()
		if mission_aborted:
			st.error(f"{result} (day {abort_day})")
		elif result and result.startswith("MISSION SUCCESS"):
			st.success(result)
		else:
			st.error(result or "Mission ended without a result.")

with data_tab:
	st.subheader("📦 Supplies")
	oxygen_column, water_column, food_column, power_column = st.columns(4)
	oxygen_column.metric("🫁 Oxygen", oxygen)
	water_column.metric("💧 Water", water)
	food_column.metric("🥫 Food", food)
	power_column.metric("🔋 Battery", f"{power}/{battery_capacity}")

	st.subheader("🧭 Mission Data")
	rover_column, science_column = st.columns(2)
	rover_column.metric("🤖 Rover data", rover_data)
	science_column.metric("🔬 Science observations", science_observations)
	if science_findings:
		for finding_day, finding in science_findings:
			st.write(f"Science finding from day {finding_day}: {finding}.")

	if show_status:
		daily_needs = calculate_daily_needs(power)
		st.subheader("Current Status Details")
		st.write(f"Oxygen: {oxygen} ({reserve_label(oxygen)})")
		st.write(f"Water: {water} ({reserve_label(water)})")
		st.write(f"Food: {food} ({reserve_label(food)})")
		st.write(f"Battery: {power}/{battery_capacity} ({reserve_label(power)})")
		st.write(f"Water recycler: {daily_needs['recycler_status']}")
		st.write(f"Net water needed per shift: {daily_needs['net_water_drawn']}")
		st.write(f"Solar generation today: {solar_generation_for_day(mission_day)} points")

	if show_forecast:
		st.subheader("Supply and Power Forecast")
		if mission_aborted:
			st.info("The mission is aborted; there are no normal mission days to forecast.")
		else:
			mission_days_remaining = 0 if mission_complete else mission_length - mission_day + 1
			st.write(f"Mission days remaining: {mission_days_remaining}")
			daily_needs = calculate_daily_needs(power)
			for name, amount, need in (
				("Oxygen", oxygen, daily_needs["oxygen_needed"]),
				("Water", water, daily_needs["net_water_drawn"]),
				("Food", food, daily_needs["food_needed"]),
			):
				full_days = amount // need if need else mission_days_remaining
				coverage = "COVERED" if full_days >= mission_days_remaining else "SHORTFALL"
				st.write(f"{name}: supports {full_days} full shifts; {coverage}")
			if mission_complete:
				st.info("The mission is complete; there are no normal mission days to forecast.")
			else:
				for forecast_day in build_power_forecast():
					if forecast_day["stopped"]:
						st.warning(f"Essential power cannot cover day {forecast_day['day']}; forecast stopped.")
						break
					science_note = ", optional science included" if forecast_day["science"] else ""
					st.write(
						f"Day {forecast_day['day']}: {forecast_day['solar']} solar points, "
						f"recycler {forecast_day['recycler']}, water drawn {forecast_day['water']}, "
						f"projected battery {forecast_day['battery']}/{battery_capacity}{science_note}."
					)

with systems_tab:
	st.subheader("⚙️ Mission Systems")
	st.write(f"🌱 Greenhouse: {'On' if greenhouse_enabled else 'Off'} ({greenhouse_grow_shifts}/{greenhouse_harvest_after} shifts toward harvest)")
	st.write(f"🔬 Science instrument requested: {'Yes' if optional_science_enabled else 'No'}")
	st.write(f"☀️ Solar generation today: {solar_generation_for_day(mission_day)} points")
	st.write(f"🧰 Solar repair kit available: {'Yes' if repair_kit_available else 'No'}")
	st.write(f"🛠️ Solar repair pending: {'Yes' if repair_pending else 'No'}")
	st.write(f"📡 Emergency help pending: {'Yes' if delivery_pending else 'No'}")
	if show_guide:
		st.subheader("📖 Game Guide")
		st.write("Finish the planned shifts with enough oxygen, water, food, battery, and rover data to earn a medal.")
		st.write("The recycler recovers half the water and uses 1 battery point only when the battery is above the warning line. Otherwise, it pauses.")
		st.write("Greenhouse costs 2 water and 2 battery points on each successful shift. Three successful shifts add 10 food points.")
		st.write("Solar-generation days are randomized. An unrepaired solar fault stops solar generation from day 3; request repair on or after day 3, then a successful shift uses the repair kit and 2 battery points.")
		st.write("Science uses 6 battery points and records one fictional finding when it runs. It is unavailable on day 5 and pauses if it would cross the critical battery line.")
		st.write("A rover survey costs 8 battery points, is unavailable on shadow days, and has a 70% chance of adding one rover data point.")
		st.write("If oxygen, water, or food is at or below the critical line after a shift, you can trade 20 battery points for 15 points of that supply, if the battery stays at or above the critical line.")
		st.write("Day 5 may require typing HELP within 10 seconds. Other eligible shifts have a 20% chance of requiring REPAIR within 10 seconds. Emergency help costs 10 battery points, repairs equipment, and delivers no supplies.")
		st.write("If a shift cannot cover essential needs, or a required reserve reaches zero, the mission stops.")
		st.write(f"Medals require at least {medal_data['Bronze']} rover data for Bronze, with higher targets for Silver and Gold. Each main supply and battery must finish above {supply_minimum}.")

with log_tab:
	st.subheader("📝 Mission Log")
	with st.form("mission_note_form", clear_on_submit=True):
		note_text = st.text_area("✍️ Write a mission note", disabled=pending_response)
		save_note = st.form_submit_button("💾 Save mission note", disabled=pending_response)
	if save_note:
		if note_text.strip():
			mission_log.append((mission_day, note_text.strip()))
			st.success("Mission note saved.")
			save_game_state()
		else:
			st.info("Write a note before saving it.")
	if mission_log:
		for note_number, (note_day, note) in enumerate(mission_log, start=1):
			st.write(f"{note_number}. Day {note_day}: {note}")
	else:
		st.info("No mission notes have been written.")

with history_tab:
	st.subheader("📚 Mission History")
	st.write("Each row is a mission day. Positive numbers were added; negative numbers were used.")
	if mission_history:
		resources = ("Oxygen", "Water", "Food", "Battery")
		changes_by_day = {}
		notes_by_day = {}
		for entry in mission_history:
			day = entry["day"]
			if day not in changes_by_day:
				changes_by_day[day] = {resource: [] for resource in resources}
				notes_by_day[day] = []
			for change in entry["changes"]:
				amount = change["amount"]
				if amount > 0:
					change_text = f"+{amount} ({change['reason']})"
				else:
					change_text = f"−{abs(amount)} ({change['reason']})"
				changes_by_day[day][change["resource"]].append(change_text)
			notes_by_day[day].extend(entry["notes"])

		table_rows = []
		for day in sorted(changes_by_day):
			row = {"Day": f"Day {day}"}
			for resource in resources:
				resource_changes = changes_by_day[day][resource]
				row[resource] = "; ".join(resource_changes) if resource_changes else "No change"
			table_rows.append(row)
		st.table(table_rows)

		with st.expander("Shift events and notes"):
			for day in sorted(notes_by_day):
				for note in notes_by_day[day]:
					st.write(f"Day {day}: {note}")
	else:
		st.info("No shifts have been recorded yet. Simulate a shift to begin your mission history.")
