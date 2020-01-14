source ./variables_common.tcl
source ./variables_adder.tcl
source ./proc_place_route.tcl
source ./proc_misc.tcl

set_cpu
delete_warnings

proc backend_clb {} {
	global vars
	import_design_backend
	#timeDesign -prePlace -expandedViews -outDir $vars(rpt_dir) -prefix $vars(design)
	floorplan_design
	place_core_cells
	#timeDesign -preCTS -expandedViews -outDir $vars(rpt_dir) -prefix $vars(design)
	#report_extract_timing_clb place
	route_core_cells
	#setExtractRCMode -engine postRoute
	#timeDesign -postRoute -expandedViews -outDir $vars(rpt_dir) -prefix $vars(design)
	optdesign_post_route
	#correct_antenna
	add_filler_cells
	verify_design
	sta_report_timing
	#export_design
}

backend_clb
