import yagmail
from keys import *
from satellite_pass import *

def get_headline():
    headline = f"<h3>Update for {datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S %Z')}</h3>"
    return headline

def send_status(sat):
    yag = yagmail.SMTP(DEV_ACCT, DEV_PW)
    contents = [get_headline(), sat.get_all_html()]
    yag.send(sat.recipient,
      f"Tracking {sat.satellite_name} passes above {sat.address}",
       contents)

def send_failure(sat):
    yag = yagmail.SMTP(DEV_ACCT, DEV_PW)
    failed = f"Thank you for submitting a tracking request for <strong>{sat.satellite_name}</strong>. "
    failed = failed + f"Unfortunately, {sat.satellite_name} will not be making any passes within the next 5 days."
    failed = failed + f"Please select a different satellite to track or try again later."
    contents = [failed]
    yag.send(sat.recipient,
      f"Tracking {sat.satellite_name} passes above {sat.address}",
       contents)

def send_concluded(sat):
    yag = yagmail.SMTP(DEV_ACCT, DEV_PW)
    concluded = f"This is to inform you that {sat.satellite_name}</strong> has completed the final pass during the requested time span. "
    concluded = concluded + f"To continue receiving updates, please submit a new request."
    contents = [concluded]
    yag.send(sat.recipient,
      f"Tracking {sat.satellite_name} passes above {sat.address}",
       contents)  

def send_welcome(sat):

    greeting = f"<p>Welcome to the satellite tracker!</p><p>Thank you for submitting a tracking request for <strong>{sat.satellite_name}</strong>. "
    greeting = greeting + f"Over the next 5 days, {sat.satellite_name} will make {sat.pass_count} passes above {sat.address}.</p><p>"
    
    s = 0
    while s < len(sat.passes):
        pass_time = datetime.utcfromtimestamp(int(sat.passes[s].get("startUTC"))).strftime("%Y-%m-%d %H:%M:%S %Z")
        greeting = greeting + f"Pass {s +1} will occur at {pass_time}\n"
        s += 1

    greeting = greeting + f"</p><p>You will receive notifications before each pass containing updated information regarding the viewing conditions."
    greeting = greeting + f"All times are UTC. Your first update will arrive shortly.</p>"

    yag = yagmail.SMTP(DEV_ACCT, DEV_PW)
    contents = [greeting]

    yag.send(sat.recipient,
      f"Tracking {sat.satellite_name} passes above {sat.address}",
       contents)


if __name__ == "__main__":


    s = Satellite_Pass("Seattle, WA", RECIPIENT, SATELLITES.get("NEPALISAT1"))
    s.get_location_data()
    s.get_elevation()
    s.get_visual_passes()
    s.get_forecast()
    s.get_lunar_data()
    s.get_twilight_data()
    send_welcome(s)
    send_status(s)
  


