# ####################################################################

#  Created by Genus(TM) Synthesis Solution 19.11-s087_1 on Sat Nov 09 15:10:31 MST 2019

# ####################################################################

set sdc_version 2.0

set_units -capacitance 1fF
set_units -time 1ps

# Set the current design
current_design ${DESIGN}

set_clock_gating_check -setup 0.0 
set_wire_load_mode "enclosed"
