##########################
#  FPGA characteristics  #
##########################
set vars(benchmark)				inv_bench
set vars(fpga_width)			2
set vars(fpga_height)			2


set vars(aspect_ratio)			[expr {double($vars(fpga_height))/$vars(fpga_width)}]


set vars(ble_number) 			10
set vars(io_number)				8
set vars(celltype)				SC
	#SC or FC
set vars(corners_list)			"wc bc"
set vars(setup_corners)			"wc"
set vars(muxtype)				sc
	#sc, tgate or muxopt or rram
set vars(techtype)				sram
set vars(configtype)			scan_chain
	#rram_decoder scan_chain memory_bank
set vars(archtype)				stratix4_k8_N10
set vars(fpga_fullname)			$vars(benchmark)_$vars(techtype)_$vars(configtype)_$vars(celltype)_$vars(archtype)_$vars(fpga_width)x$vars(fpga_height)_eri2019
set vars(projectname_top)		$vars(fpga_fullname)_$vars(muxtype)

##########################
#  Technology variables  #
##########################
set vars(process) 				28
set vars(foundry)				asap
set vars(node)					$vars(foundry)$vars(process)
	#_stratix4
set vars(filler_cells) 			"FILLER_ASAP7_75t_R FILLERxp5_ASAP7_75t_R"
set vars(tie_cells)				"TIEHIx1_ASAP7_75t_R TIELOx1_ASAP7_75t_R"
set vars(tap_cell)				"TAPCELL_ASAP7_75t_R"
set vars(antenna_cell)			""
set vars(cts_buffer_cells)		"BUFx2_ASAP7_75t_R BUFx3_ASAP7_75t_R BUFx4_ASAP7_75t_R BUFx5_ASAP7_75t_R BUFx8_ASAP7_75t_R BUFx10_ASAP7_75t_R BUFx12_ASAP7_75t_R BUFx24_ASAP7_75t_R"
set vars(cts_inverter_cells)	"INVx1_ASAP7_75t_R INVx2_ASAP7_75t_R INVx3_ASAP7_75t_R INVx4_ASAP7_75t_R INVx5_ASAP7_75t_R INVx6_ASAP7_75t_R INVx8_ASAP7_75t_R INVx11_ASAP7_75t_R INVx13_ASAP7_75t_R"
#Need to get the minimum IO filler width so the spacing between 2 pads is a multiple
set vars(io_min_spacing)		0.1
#Order is important: From bigger to smaller (the script will place the bigger first etc).
set vars(iofiller_cells)		""

set vars(site_name)				"coreSite"
set vars(low_metal_name)		"M1(1)"
set vars(high_metal_name)		"M9(9)"
set vars(power_nets_sclib)		"VDD"
set vars(ground_nets_sclib)		"VSS"

########################
#  Backend file paths  #
########################
set vars(current_folder)			[pwd]
set vars(working_dir)				"$vars(current_folder)"
set vars(scripts_dir)				"$vars(working_dir)/scripts"
set vars(common_scripts_dir)		"$vars(scripts_dir)/common_scripts"
set vars(common_scripts_python_dir)	"$vars(common_scripts_dir)/python"
set vars(tmp_dir)					"$vars(scripts_dir)/tmp_files"
#set vars(posh_shared_path)			"/var/tmp/POSH/innovus_files/$vars(node)"

set vars(pdk_path)					"/research/ece/lnis/CAD_TOOLS/DKITS/ASAP7_PDKandLIB_v1p5/asap7libs_24"
#set vars(pdk_path)					"/research/ece/lnis/CAD_TOOLS/DKITS/ASAP7/ASAP7_PDKandLIB_v1p6/asap7_7p5t_library"
set vars(tech_path)					"$vars(pdk_path)/techlef_misc"
set vars(qrc_path)					"$vars(pdk_path)/qrc"

set vars(sc_lib_path)				"$vars(pdk_path)/lib"
set vars(sc_lef_path)				"$vars(pdk_path)/lef/scaled"
#set vars(vpr_path)					"$vars(posh_shared_path)/VPR_FILES/$vars(fpga_fullname)"
#set vars(verilog_fullpath)			"$vars(vpr_path)/SRC"
set vars(tcl_fullpath)				"$vars(current_folder)/SCRIPTS"
set vars(sdc_fullpath)				"$vars(current_folder)/SDC"
set vars(rpt_fullpath)				"$vars(current_folder)/RPT"

set vars(lef_files)					"$vars(tech_path)/asap7_tech_4x_170803.lef \
									$vars(sc_lef_path)/asap7sc7p5t_24_R_4x_170912.lef"

#set vars(lef_files)					"$vars(tech_path)/asap7_tech_4x_170803.lef \
#									$vars(sc_lef_path)/asap7sc7p5t_24_L_4x_170912.lef \
#									$vars(sc_lef_path)/asap7sc7p5t_24_R_4x_170912.lef \
#									$vars(sc_lef_path)/asap7sc7p5t_24_SL_4x_170912.lef \
#									$vars(sc_lef_path)/asap7sc7p5t_24_SRAM_4x_170912.lef"

set vars(wc_timing) 				"$vars(sc_lib_path)/asap7sc7p5t_24_AO_RVT_SS.lib $vars(sc_lib_path)/asap7sc7p5t_24_INVBUF_RVT_SS.lib $vars(sc_lib_path)/asap7sc7p5t_24_OA_RVT_SS.lib $vars(sc_lib_path)/asap7sc7p5t_24_SIMPLE_RVT_SS.lib $vars(sc_lib_path)/asap7sc7p5t_24_SEQ_RVT_SS.lib"
set vars(bc_timing) 				"$vars(sc_lib_path)/asap7sc7p5t_24_AO_RVT_FF.lib $vars(sc_lib_path)/asap7sc7p5t_24_INVBUF_RVT_FF.lib $vars(sc_lib_path)/asap7sc7p5t_24_OA_RVT_FF.lib $vars(sc_lib_path)/asap7sc7p5t_24_SIMPLE_RVT_FF.lib $vars(sc_lib_path)/asap7sc7p5t_24_SEQ_RVT_FF.lib"

#set vars(wc_timing) 				"$vars(sc_lib_path)/asap7sc7p5t_AO_RVT_SS_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_INVBUF_RVT_SS_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_OA_RVT_SS_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_SEQ_RVT_SS_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_SIMPLE_RVT_SS_08302018.lib"
#set vars(bc_timing) 				"$vars(sc_lib_path)/asap7sc7p5t_AO_RVT_FF_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_INVBUF_RVT_FF_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_OA_RVT_FF_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_SEQ_RVT_FF_08302018.lib $vars(sc_lib_path)/asap7sc7p5t_SIMPLE_RVT_FF_08302018.lib"

set vars(wc_qrc)                	"$vars(qrc_path)/qrcTechFile_typ03_scaled4xV06"
set vars(bc_qrc)					"$vars(qrc_path)/qrcTechFile_typ03_scaled4xV06"

set vars(mmmc_file)					"$vars(working_dir)/COMMON/CONF/fpga.view"
set vars(fpga_globals_file)			"$vars(working_dir)/COMMON/CONF/fpga.globals"

#set vars(qrc_map_file)				"$vars(qrc_path)/qrc_innovus.map"
#set vars(map_file) 					"$vars(SC_path)/sef/digital/Back_End/lef/tcbn45gsbwp_120b/techfiles/gds2.map"

#############################
#  Analysis configurations  #
#############################
set vars(wc_corner_name)		"wc"
set vars(bc_corner_name)		"bc"
set vars(tc_corner_name)		"tc"
set vars(wc_lib_name)			"wc"
set vars(bc_lib_name)			"bc"
set vars(tc_lib_name)			"tc"
set vars(wc_delay_name)			"wc"
set vars(bc_delay_name)			"bc"
set vars(tc_delay_name)			"tc"
set vars(wc_analysis_name)		"wc"
set vars(bc_analysis_name)		"bc"
set vars(tc_analysis_name)		"tc"
set vars(constraint_name)		"constraint"
