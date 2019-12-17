from satellite_pass import *
from notifier import *
from keys import *
import time


SKY_EVENT = "http://localhost:8080/sky/event/"
SKY_CLOUD = "http://localhost:8080/sky/cloud/"

def check_for_tracking_request():
	url = f"{SKY_CLOUD}{ECI}/satellite/tracking"
	response = requests.get(url).json()
	return response


def clear_tracking_request():
	url = f"{SKY_EVENT}{ECI}/999/satellite/reset_request"
	response = requests.post(url).json()
	#pprint(response)

def trigger_welcome(current_response):
	email = current_response[0].get("email")
	address = current_response[0].get("address")
	satellite = current_response[0].get("sat_name")

	try:
		sat = Satellite_Pass(address, email, satellite)
		sat.get_location_data()
		sat.get_elevation()
		sat.get_visual_passes()
		sat.get_forecast()
		sat.get_lunar_data()
		sat.get_twilight_data()
		send_welcome(sat)

	except:
		send_failure(sat)
		clear_tracking_request()
		return

	if sat.passes:
		trigger_notifications(sat, current_response)
	else:
		send_failure(sat)
		clear_tracking_request()
		return


def trigger_notifications(sat, current_response):
	first_sent = False
	second_sent = False
	while len(sat.passes) > 0:
		print("\nNotification sender:\n")
		time_to_pass = (sat.next_pass[0] - int(time.time())) // 60
		print(f"{time_to_pass} minutes until next pass")
		#send the first notification right away
		if first_sent == False:
			send_status(sat)
			print("\nSent first notification")
			first_sent = True
		#send the second notification an hour before the pass
		if int(time.time()) > sat.next_pass[0]- 3600 and second_sent == False:
			send_status(sat)
			print("\nSent second notification")
			second_sent = True
		#if the pass is over, queue the next pass
		if int(time.time()) > sat.next_pass[1]:
			first_sent = False
			second_sent = False
			sat.passes.pop(0)
			if len(sat.passes) == 0:
				print("Finished")
				send_concluded(sat)
				clear_tracking_request()
				return
			else:
				print("Queing next pass")
				sat.next_pass = (sat.passes[0].get("startUTC"), sat.passes[0].get("endUTC"),)
				sat.get_forecast()
				sat.get_lunar_data()
				sat.get_twilight_data()

		new_response = check_for_tracking_request()
		print("\nCurrent Response:")
		pprint(current_response)
		print("\nNew Response:")
		pprint(new_response)
		
		if current_response != check_for_tracking_request():
			print("\nNew tracking request found, exiting current")
			return
		else:
			print("\nNo new tracking request found")
			print("\n********************")
			time.sleep(5)
		

def listen_for_requests():
	previous_response = None
	while True:
		time.sleep(5)
		current_response = check_for_tracking_request()
		print("\nMain Listener:\n")
		print("\nCurrent Response:")
		pprint(current_response)
		print("\nPrevious Response:")
		pprint(previous_response)
		
		if current_response == previous_response:
			print("\nNo new tracking request found")
			print("\n********************")
			continue
		else:
			previous_response = current_response
			if current_response != None:
				print("\nNew tracking request found")
				trigger_welcome(current_response)

if __name__=="__main__":
	listen_for_requests()

