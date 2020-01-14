##########################
#  Module/Project names  #
##########################
set vars(design)				 	mem_ctrl
set vars(topmodule)					mem_ctrl


###########
#  Modes  #
###########
set vars(sta)						"no"
set vars(cpf)						"no"
set vars(place_opt)					"no"
set vars(cts_concurrent_opt)		"no"

####################
#  Path variables  #
####################
set vars(dbs_dir) 					./DBS/$vars(design)
set vars(rpt_dir)					./RPT/$vars(design)
set vars(rpt_dir_timings)			$vars(rpt_dir)/timing_reports
set vars(rpt_dir_summary)			$vars(rpt_dir)/timing_summary
set vars(script_dir)				./scripts
#set vars(constraint_sdc_path) 		"$vars(working_dir)/COMMON/SDC/constraint_clb_$vars(mux_type).sdc"
set vars(constraint_sdc_path) 		"mem_ctrl_map.sdc"
set vars(verilog_files)				"mapped.v"

####################
#  FP constraints  #
####################
#For additional global pads (set/reset) and power grounds. If none are used, set vars to 0.
set vars(additional_pads)			0
set vars(corner_enable)				"false"
set vars(core_to_pads)				8
set vars(ring_width)				2
set vars(ring_spacing)				1
#set vars(stripe_width)				4
#set vars(stripe_spacing)			2


######################
#  Design variables  #
######################
set vars(density)					0.55
set vars(power_nets)        		VDD
set vars(ground_nets)         		VSS
set vars(left_ring_metal)			"M6"
set vars(right_ring_metal)			"M6"
set vars(top_ring_metal)			"M7"
set vars(bottom_ring_metal)			"M7"


#########################
#  Routing constraints  #
#########################
set vars(max_route_layer)			9
set vars(min_route_layer)			2
set vars(congestion_effort)			high
set vars(route_fix_antenna)			true
set vars(route_insert_antenna)		true
set vars(route_si)					true
set vars(route_timing)				true
set vars(route_tdr_effort)			5


###################
#  Miscellaneous  #
###################
set vars(cpu_number)  				32
set init_design_uniquify 			1
