ruleset satellite {

	meta {
		provides tracking

		shares tracking
	}

	global {
		tracking = function() {
			ent:tracking_profile
		}
	}

	rule new_tracking {
		select when satellite track_request 
		pre {
			sat_name = event:attr("sat_name")
			address = event:attr("address")
			email = event:attr("email")
		}
		always {
			ent:tracking_profile := [{"sat_name":sat_name, "address":address, "email":email}]
		}
	}

	rule clear_tracking {
		select when satellite reset_request
		always {
			clear ent:tracking_profile
		}
	}
}