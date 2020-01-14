################################################################################
# Configs
################################################################################
set DESIGN    _CKT_NAME_
set COMB      _CKT_COMB_
set TARGET_CT _TARGET_CT_

include load.tcl

read_hdl  ${DESIGN}.v
elaborate ${DESIGN}

if $COMB {
	create_clock -period ${TARGET_CT} [get_ports clock]
} else {
	set_max_delay -from [all_inputs] -to [all_outputs] 100
}

syn_generic
syn_map
syn_opt -incremental

exit
