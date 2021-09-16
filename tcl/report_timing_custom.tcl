proc custom_report_timing {} {
	global vars

	report_area > ./FinalRPTs/##area_##.rpt
	report_power > ./FinalRPTs/##power_##.rpt
	report_timing -path_type summary > ./FinalRPTs/##summary_##.rpt
	
	report_timing -format {timing_point flags arc edge cell fanout load delay arrival instance_location} -max_paths 999999 > ./FinalRPTs/##timing_##.rpt
	
	set pathDict {}
	foreach startpoint [get_object_name [all_inputs]] { 
		set full_endPointList []
		foreach endpointList [get_object_name [get_cells -of_objects [filter_collection [all_fanout -from $startpoint -endpoints_only -flat] "object_type==pin"]]] {
			foreach endpoint $endpointList {
				if { $endpoint != $startpoint } {
					lappend full_endPointList $endpoint
				}
			}
		}
		foreach endpointList [get_object_name [filter_collection [all_fanout -from $startpoint -endpoints_only -flat] "object_type!=pin"]] {
			foreach endpoint $endpointList {
				if { $endpoint != $startpoint } {		
					lappend full_endPointList $endpoint
				}
			}
		}
		dict set pathDict $startpoint $full_endPointList 
	}

	set regDict {}
	foreach startpoint [get_object_name [all_registers]] { 
		set full_endPointList []
		set pin [get_object_name [get_pins -of_objects $startpoint -filter "is_clock_pin==true"]]
		foreach endpointList [get_object_name [get_cells -of_objects [filter_collection [all_fanout -from $pin -endpoints_only -flat] "object_type==pin"]]] {
			foreach endpoint $endpointList {
				if { $endpoint != $pin } {
					lappend full_endPointList $endpoint
				}
			}
		}
		foreach endpointList [get_object_name [filter_collection [all_fanout -from $pin -endpoints_only -flat] "object_type!=pin"]] {
			foreach endpoint $endpointList {
				if { $endpoint != $pin } {
					lappend full_endPointList $endpoint
				}
			}
		}
		dict set regDict $startpoint $full_endPointList 
	}

	dict for {key value} $pathDict { foreach v $value { report_timing -format {timing_point flags arc edge cell fanout load delay arrival instance_location} -from $key -to $v >> ./FinalRPTs/timing_by_pairs.rpt }}
	dict for {key value} $regDict {  foreach v $value { report_timing -format {timing_point flags arc edge cell fanout load delay arrival instance_location} -from $key -to $v >> ./FinalRPTs/timing_by_pairs.rpt }}
}

