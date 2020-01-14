proc put_header hdr {
	puts "\n---#-----------------------------------------------------"
	puts "---# $hdr"
	puts "---#-----------------------------------------------------\n"
}


proc save_design step {
	global vars
	saveDesign $vars(dbs_dir)/$vars(projectname_top)/$step.enc
}


proc restore_design step {
	global vars
	restoreDesign $vars(dbs_dir)/$vars(projectname_top)/$step.enc.dat $vars(design)
	set_analysismode
	set_optmode
}


proc set_cpu {} {
	global vars
	setMultiCpuUsage -localCpu $vars(cpu_number) -keepLicense true -acquireLicense $vars(cpu_number)
}



proc import_design_backend {} {
	global vars

	if { $vars(sta) == "yes" } {
		read_view_definition $vars(mmmc_file_sta)
		read_verilog $vars(verilog_files_sta)
		set_top_module $vars(design) -ignore_undefined_cell
		foreach corner $vars(corners_list) {read_spef $vars(spef_${corner}_sta) -rc_corner $vars(${corner}_corner_name)}
		setDesignMode -process $vars(process)
		} else {

			uplevel #0 source $vars(fpga_globals_file)
			init_design

			if { $vars(cpf) == "yes" } {
				read_power_intent -cpf $vars(cpf_file)
				commit_power_intent }
			set_analysismode
			set_optmode
			save_design init
			}
}



proc set_optmode {} {
	setOptMode -deleteInst false -reclaimArea false -simplifyNetlist false
}

proc set_analysismode {} {
	global vars
	setDesignMode -process $vars(process)
}


proc define_floorplan {} {
	global vars

	floorPlan -site $vars(site_name) -r 1 $vars(density) $vars(core_to_pads) $vars(core_to_pads) $vars(core_to_pads) $vars(core_to_pads)

	globalNetConnect $vars(power_nets) -type pgpin -pin $vars(power_nets_sclib) -inst * -module {}
	globalNetConnect $vars(ground_nets) -type pgpin -pin $vars(ground_nets_sclib) -inst * -module {}
}



proc create_special_route {} {
	global vars
	set powerground_nets "$vars(power_nets) $vars(ground_nets)"
	set metal_bounds "$vars(low_metal_name) $vars(high_metal_name)"

	#VDD/VSS for core
	sroute -connect { corePin } -layerChangeRange $metal_bounds -corePinTarget { firstAfterRowEnd } -allowJogging 1 -crossoverViaLayerRange $metal_bounds -nets $powerground_nets -allowLayerChange 0 -targetViaLayerRange $metal_bounds -deleteExistingRoutes	
}


proc add_rings {} {
	global vars
	set power_nets "$vars(power_nets) $vars(ground_nets)"
	set layers "top $vars(top_ring_metal) bottom $vars(bottom_ring_metal) left $vars(left_ring_metal) right $vars(right_ring_metal)"

	#Add ring around core
addRing -nets $power_nets -type core_rings -follow core -layer $layers -width "top $vars(ring_width) bottom $vars(ring_width) left $vars(ring_width) right $vars(ring_width)" -spacing "top $vars(ring_spacing) bottom $vars(ring_spacing) left $vars(ring_spacing) right $vars(ring_spacing)" -center 1
}



proc add_stripes {} {
	global vars
	set power_nets "$vars(power_nets) $vars(ground_nets)"
	set coreBoxWidth [dbGet top.fplan.coreBox_sizex]
	set stripes_width_total [expr {2*$vars(stripe_width)+$vars(stripe_spacing)}]
	set fp_row_sizey [lindex [dbGet top.fPlan.rows.site.size_y] 0]
	set spacing [expr {($coreBoxWidth/($vars(stripe_number)+1))+$stripes_width_total}]
	#We round the spacing variable to me a multiple of the x grid
	set spacing [expr round($spacing/$fp_row_sizey)*$fp_row_sizey]
	set start [expr ($coreBoxWidth/($vars(stripe_number)+1))-($stripes_width_total/($vars(stripe_number)+1))]

	addStripe -nets $power_nets -layer $vars(stripe_vert_metal) -direction vertical -width $vars(stripe_width) -spacing $vars(stripe_spacing) -start_from left -start_offset $start -snap_wire_center_to_grid None -set_to_set_distance $spacing
}


proc add_tapcells {} {
	global vars
	set fp_row_sizex [lindex [dbGet top.fPlan.rows.site.size_x] 0]
	set tappcell_distance_total [expr {$fp_row_sizex*$vars(tapcell_distance)}]
	addWellTap -cell $vars(tap_cell) -cellInterval $tappcell_distance_total
}


proc floorplan_design {} {
	global vars

	define_floorplan
	add_rings
	create_special_route
	save_design fplan
}


proc add_iofiller_cells {} {
	#global design
	global rpt_dir
	global vars
	put_header "Adding IO filler cells..."

	set prefix FILLER
	set number_io_fill [llength $vars(iofiller_cells)]
	set number_io_fill_decr [expr {$number_io_fill-1}]

	#If there is only one IO, go to the else. Generally not the case
	if {$number_io_fill>2} {
		foreach {side} [list n s e w] {
			for {set x 0} {$x<$number_io_fill_decr} {incr x} {
				set io_filler [lindex $vars(iofiller_cells) $x]
				addIoFiller -cell $io_filler -prefix $prefix -side $side
			}
			set io_filler_last [lindex $vars(iofiller_cells) $number_io_fill_decr]
			addIoFiller -cell $io_filler_last -prefix $prefix -side $side -fillAnyGap

		} 
	} else {
			foreach {side} [list n s e w] {
				for {set x 0} {$x<$number_io_fill_decr} {incr x} {
					set io_filler [lindex $vars(iofiller_cells) $x]
					addIoFiller -cell $vars(iofiller_cells) -prefix $prefix -side $side -fillAnyGap
				}
			}
		}
}


proc add_tiecells {} {
	global vars
	setTieHiLoMode -cell $vars(tie_cells)
	addTieHiLo
}

	
proc place_core_cells {} {
	global vars
	put_header "Placing core cells..."

	setRouteMode -earlyGlobalMaxRouteLayer $vars(max_route_layer)
	#setNanoRouteMode -routeTopRoutingLayer $max_route_layer
	#setNanoRouteMode -routeBottomRoutingLayer $min_route_layer

	#setMaxRouteLayer $vars(max_route_layer)
	setPlaceMode -place_global_cong_effort $vars(congestion_effort) -place_global_place_io_pins 1

	if {$vars(place_opt) == "yes" } {place_opt_design -prefix place -out_dir $vars(rpt_dir)} else {place_design -noPrePlaceOpt}
	#-noPrePlaceOpt

	add_tiecells
	checkPlace $vars(rpt_dir)/checkplace_place_pre_refine.rpt
	refinePlace
	checkPlace $vars(rpt_dir)/checkplace_place_post_refine.rpt	
	save_design place
}


proc optdesign_prects_drvonly {} {
	global vars
	setCTSMode -routeBottomPreferredLayer $vars(min_route_layer)
	optDesign -preCTS -drv -outDir $vars(rpt_dir) -prefix pretcts
	refinePlace
	save_design opt_prects
}


proc optdesign_prects {} {
	global vars
	setCTSMode -routeBottomPreferredLayer $vars(min_route_layer)
	optDesign -preCTS -outDir $vars(rpt_dir) -prefix pretcts
	refinePlace
	save_design opt_prects
}


proc create_clock_tree {} {
	global vars
 
	setAnalysisMode -analysisType onChipVariation -cppr both

	put_header "Creating clock tree..."
	create_route_type -name clkroute -top_preferred_layer $vars(max_route_layer)

	set_ccopt_property route_type clkroute -net_type trunk
	set_ccopt_property route_type clkroute -net_type leaf
	set_ccopt_property buffer_cells $vars(cts_buffer_cells)
	set_ccopt_property inverter_cells $vars(cts_inverter_cells)

	create_ccopt_clock_tree_spec -file ccopt.spec
	source ccopt.spec

	#Enable clock concurent optimization (does datapath opt. and useful skew): remove -cts
	if {$vars(cts_concurrent_opt) == "yes" } {ccopt_design} else {ccopt_design -cts}
	save_design cts
}


proc check_design {} {
check_timing -type loops -verbose
checkPlace
}


proc optdesign_post_cts {} {
	global vars
	optDesign -postCTS -hold -setup -outDir $vars(rpt_dir) -prefix postcts
	refinePlace
	save_design potscts_opt
}


proc optdesign_postcts_holdonly {} {
	global vars
	optDesign -postCTS -hold -outDir $vars(rpt_dir) -prefix postcts
	refinePlace
	save_design opt_postcts
}


proc route_core_cells {} {
	global vars

	setNanoRouteMode -routeTopRoutingLayer $vars(max_route_layer) \
		-routeWithTimingDriven $vars(route_timing) \
		-routeTdrEffort $vars(route_tdr_effort) \
		-drouteFixAntenna $vars(route_fix_antenna) -routeInsertAntennaDiode $vars(route_insert_antenna) -routeAntennaCellName $vars(antenna_cell) \
		-routeWithSiDriven $vars(route_si)
	routeDesign
	# -globalDetail

	#checkRoute

	save_design route
}


proc add_filler_cells {} {
	global vars

	put_header "Adding filler cells..."
	addFiller -cell $vars(filler_cells) -prefix FILLER

	save_design filled
}


proc remove_halo {} {
	#Need to remove halo around blocks before adding fillers
	deleteHaloFromBlock -allBlock
}


proc optdesign_post_route {} {
	global vars
	setAnalysisMode -analysisType onChipVariation -cppr both
	optDesign -postRoute -outDir $vars(rpt_dir) -prefix postroute -setup -hold  
	save_design route_opt
}


proc optdesign_post_route_drv_only {} {
	global vars
	setAnalysisMode -analysisType onChipVariation -cppr both
	optDesign -postRoute -outDir $vars(rpt_dir) -prefix postroute -drv
	save_design postroute_opt

}


proc verify_design {} {
	global vars

	put_header "Verifying design..."

	verifyConnectivity -type all -report $vars(rpt_dir)/$vars(design)_connectivity.rpt
	verifyGeometry -report $vars(rpt_dir)/$vars(design)_geometry.rpt

	save_design verify
}


proc time_design_step {step} {
	global vars

	if {$step == "postRoute"} { setAnalysisMode -analysisType onChipVariation -cppr both
	setExtractRCMode -effortLevel high -engine postRoute
	} else {}
	timeDesign -outDir $vars(rpt_dir) -prefix $vars(projectname) -$step

	if {$step == "signoff"} { setAnalysisMode -analysisType onChipVariation -cppr both
	setExtractRCMode -lefTechFileMap $vars(qrc_map_file) -effortLevel $step -engine postRoute
	} else {}
	timeDesign -outDir $vars(rpt_dir) -prefix $vars(projectname) -$step
}


#Verify antenna and add diodes if antenna violation.
proc correct_antenna {} {
	global vars

	set antenna_rpt_file $vars(rpt_dir)/$vars(projectname)_processantenna.rpt

	verifyProcessAntenna -report $antenna_rpt_file
	addDiode $antenna_rpt_file $vars(antenna_cell)

	save_design antenna
}


proc add_metal_fill {} {
	addMetalFill
	save_design metalfilled
}


proc generate_reports {step} {
	global vars

	put_header "Generating reports..."

	reportNetStat > $vars(rpt_dir)/$vars(projectname)_netlist_stats_$step.rpt
	report_area > $vars(rpt_dir)/$vars(projectname)_area_$step.rpt
	summaryReport -noHtml -outfile $vars(rpt_dir)/$vars(projectname)_summary_$step.rpt
	#report_power -outfile $vars(rpt_dir)/$vars(projectname)_power_$step.rpt -view $vars(wc_corner_name) -instances $vars(topmodule_fpga)/*
	#if {$vars(design) == "$vars(benchmark)_top" } {python_area_posh}
	#setAnalysisMode -analysisType onChipVariation
	#setAnalysisMode -cppr both
}

proc sta_report_timing {} {
	global vars
	report_timing -format {timing_point flags arc edge cell fanout load delay arrival instance_location} -max_paths 2147483647 > ./sweep_timing_PR_450.rpt
}



proc export_design {} {
	global vars

	put_header "Exporting design..."

	#Export netlist
	saveNetlist -excludeLeafCell "$vars(working_dir)/VERILOG/$vars(projectname).v"
	#saveNetlist -excludeLeafCell -exclude_cell_def $vars(clb_design) "VERILOG/$vars(projectname).v"

	#Export the SDC (the original one can not be read with primetime since it uses innovus commands)
	write_sdc "$vars(working_dir)/SDC/$vars(projectname)_post_pr.sdc"

	#Export the parasitics SPEF file for STA
	setExtractRCMode -lefTechFileMap $vars(qrc_map_file) -effortLevel signoff -engine postRoute
	extractRC
	foreach corner $vars(corners_list) {rcOut -spef $vars(working_dir)/SPEF/$vars(projectname)_post_pr_${corner}.spef -rc_corner ${corner}}

	#If the design is the grid, export lef, timings
	if {$vars(design_level) == "block"} {	 
		#python3 $vars(common_scripts_python_dir)/verilog_clb_suffix.py $vars(projectname)
		#Export lib file
		foreach corner $vars(corners_list) {set_analysis_view -setup $vars(${corner}_analysis_name) -hold $vars(${corner}_analysis_name)
			spefIn -rc_corner ${corner} $vars(working_dir)/SPEF/$vars(projectname)_post_pr_${corner}.spef
			do_extract_model "$vars(working_dir)/LIB/$vars(projectname)_${corner}.lib" -view $vars(${corner}_analysis_name) -lib_name $vars(projectname)_$vars(${corner}_analysis_name)}

		#Export lef file
		#write_lef_abstract "$vars(working_dir)/LEF/$vars(projectname).lef"
		write_lef_abstract -specifyTopLayer $vars(max_route_layer) -stripePin -PGPinLayers 1 "$vars(working_dir)/LEF/$vars(projectname)_obs.lef"
		#-extractBlockPGPinLayers 1

		#Export gdsii file
		#streamOut "GDS/$vars(projectname).gds" \
					 #-mapFile $vars(map_file) \
					 #-libName $vars(projectname) \
					 #-mode ALL
	} 

#else {}	 #If the design is top level, just export GDS
		#streamOut "GDS/$vars(projectname).gds" \
					 #-mapFile $vars(map_file) \
					 #-libName $vars(projectname) \
					 #-mode ALL \
					 #-outputMacros \
					 #-merge "GDS/$vars(projectname_clb).gds $vars(sc_gds) $vars(fullcustom_gds)"

	#Copy SDC/VERILOG/SPEF files to the shared POSH folder
	#copy_files_to_posh
}


proc copy_files_to_posh {} {
	global vars

	exec cp SPEF/$vars(projectname)_post_pr_tc.spef $vars(posh_shared_path)/SPEF/$vars(projectname)_post_pr_tc.spef
	exec cp SPEF/$vars(projectname)_post_pr_bc.spef $vars(posh_shared_path)/SPEF/$vars(projectname)_post_pr_bc.spef
	exec cp SPEF/$vars(projectname)_post_pr_wc.spef $vars(posh_shared_path)/SPEF/$vars(projectname)_post_pr_wc.spef
	exec cp SDC/$vars(projectname)_post_pr.sdc $vars(posh_shared_path)/SDC/$vars(projectname)_post_pr.sdc
	if {$vars(design_level) == "block"} { exec cp VERILOG/$vars(projectname)_suffix.v $vars(posh_shared_path)/VERILOG/$vars(projectname)_suffix.v  
	} else {exec cp VERILOG/$vars(projectname).v $vars(posh_shared_path)/VERILOG/$vars(projectname).v}
}



proc backend_block {} {
	global vars
	#import_design_backend
	generate_reports init
	timeDesign -prePlace -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)
	report_extract_timing_clb init
	floorplan_design_clb
	place_core_cells
	timeDesign -preCTS -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)
	report_extract_timing_clb place
	create_clock_tree	
	timeDesign -postCTS -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)
	#timeDesign -postCTS -hold -outDir $vars(rpt_dir) -prefix $vars(projectname)
	#optDesign -postCTS -hold
	#optDesign -postCTS -expandedViews
	report_extract_timing_clb cts
	route_core_cells
	setExtractRCMode -engine postRoute
	timeDesign -postRoute -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)
	report_extract_timing_clb route
	#timeDesign -postRoute -hold -outDir $vars(rpt_dir) -prefix $vars(projectname)
	optdesign_post_route_drv_only
	correct_antenna
	delete_blockages
	add_filler_cells
	add_metal_fill
	verify_design
	#setExtractRCMode -engine postRoute -effort high
	#timeDesign
	#timeDesign -postRoute -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)

	#setExtractRCMode -engine postRoute -effort signoff
	#timeDesign -signOff -expandedViews -outDir $vars(rpt_dir) -prefix $vars(projectname)
	#Or for more accuracy: signoffTimeDesign -outDir $vars(rpt_dir) -prefix $vars(projectname)
	#report_extract_timing_clb signoff
	generate_reports signoff
	export_design
	#set_analysis_view -setup $vars(wc_analysis_name) -hold $vars(bc_analysis_name)	
}
