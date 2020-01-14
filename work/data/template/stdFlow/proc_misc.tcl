proc hierarchy_top_extra {} {
	#Check the hierarchy. If the top module is the FPGA from FPGA spice, return 1. Else (in case the user adds another top module with pads, etc), returns 0.
	global vars
	#puts "hierarchy_prefix = ${hierarchy_prefix}"
	if {$vars(hierarchy_prefix) eq ""} {

	    #puts "string is empty"
		return 1
	   #puts "string is not empty"
	} else {return 0 }
}


proc addDiode {antennaFile antennaCell} {

  unlogCommand dbGet
  if [catch {open $antennaFile r} fileId] {
    puts stderr "Cannot open $antennaFile: $fileId"
  } else {
    foreach line [split [read $fileId] \n] {
      # Search for lines matching "instName (cellName) pinName" that have violations
      if {[regexp {^  (\S+)  (\S+) (\S+)} $line] == 1} {
        # Remove extra white space
        regsub -all -- {[[:space:]]+} $line " " line
        set line [string trimlef $line]
        # Store instance and pin name to insert diodes on
        set instName [lindex [split $line] 0]
        # Modify instance name if it contains escaped characters:
        set escapedInstName ""
        foreach hier [split $instName /] {
          if {[regexp {\[|\]|\.} $hier] == 1} {
            set hier "\\$hier "
          }
          set escapedInstName "$escapedInstName$hier/"
          set instName $escapedInstName
        }
        regsub {/$} $instName {} instName
        set pinName [lindex [split $line] 2]
        set instPtr [dbGet -p top.insts.name $instName]
        set instLoc [lindex [dbGet $instPtr.pt] 0]
        if {$instName != ""} {
          # Attach diode and place at location of instance
          attachDiode -diodeCell $antennaCell -pin $instName $pinName -loc $instLoc
        }
      }
    }
  }
  close $fileId
  # Legalize placement of diodes and run ecoRoute to route them
  refinePlace -preserveRouting true
  ecoRoute
  logCommand dbGet
}

proc delete_dangling_all {} {
	#reportDanglingPort -outfile RPT/$projectname/danglingPorts_before.rpt
	#deleteEmptyModule
	deleteDanglingNet
	deleteDanglingPort
	#reportDanglingPort -outfile RPT/$projectname/danglingPorts_after.rpt
	#deleteDanglingNet
	
	}

proc even x {expr {($x % 2) == 0}}
proc odd  x {expr {($x % 2) != 0}}



proc create_boundary_routing_halo {args} {
global vars
  parse_proc_arguments -args $args options

# Halo width
set halo_width $options(-halo_width)

# Vertical routing layers
#set v_layers [dbGet [dbGet head.layers.direction Vertical -p ].name]
set v_layers $vars(vert_blockage)
# Horizontal routing layers
#set h_layers [dbGet [dbGet head.layers.direction Horizontal -p ].name]
set h_layers $vars(hor_blockage)

set h 0
set v 0
foreach i [dbShape [dbShape [dbGet top.fplan.boxes]] XOR [dbShape [dbGet top.fplan.boxes] SIZE -$halo_width] ] {
  set x1 [lindex $i 0]
  set y1 [lindex $i 1]
  set x2 [lindex $i 2]
  set y2 [lindex $i 3]

  if {[expr abs($x2 - $x1)] > [expr abs($y2 - $y1)]} {
    createRouteBlk -name HALO_ROUTING_BLOCKAGE_H -layer $h_layers -box $i -exceptpgnet
    incr h
  } else {
    createRouteBlk -name HALO_ROUTING_BLOCKAGE_V -layer $v_layers -box $i -exceptpgnet
    incr v
  }
}
  if {$h>0} {
    Puts "CDN-AE INFO: Created $h horizontal routing blockages with name HALO_ROUTING_BLOCKAGE_H - These can be removed using deleteRouteBlk -name HALO_ROUTING_BLOCKAGE_H"
  }
  if {$v>0} {
    Puts "CDN-AE INFO: Created $v vertical routing blockages with name HALO_ROUTING_BLOCKAGE_V - These can be removed using deleteRouteBlk -name HALO_ROUTING_BLOCKAGE_V"
  }
}
define_proc_arguments create_boundary_routing_halo \
  -info "Create routing blockages along block boundary\nThe blockages are in the layers perpendicular to the short dimension" \
  -define_args {
    {-halo_width "Width of the routing halo" "none" float {required}}
  }

proc delete_blockages {} {
	deleteRouteBlk -name HALO_ROUTING_BLOCKAGE_V
	deleteRouteBlk -name HALO_ROUTING_BLOCKAGE_H
}

proc create_boundary_routing_halo_forpins {args} {
  parse_proc_arguments -args $args options

# Halo width
set halo_width $options(-halo_width)

# Vertical routing layers
set layers "LY AM"



set h 0
set v 0
foreach i [dbShape [dbShape [dbGet top.fplan.boxes]] XOR [dbShape [dbGet top.fplan.boxes] SIZE -$halo_width] ] {
  set x1 [lindex $i 0]
  set y1 [lindex $i 1]
  set x2 [lindex $i 2]
  set y2 [lindex $i 3]

  if {[expr abs($x2 - $x1)] > [expr abs($y2 - $y1)]} {
    createRouteBlk -name HALO_ROUTING_BLOCKAGE_H -layer $layers -box $i -exceptpgnet
    incr h
  } else {
    createRouteBlk -name HALO_ROUTING_BLOCKAGE_V -layer $layers -box $i -exceptpgnet
    incr v
  }
}

}
define_proc_arguments create_boundary_routing_halo_forpins \
  -info "Create routing blockages along block boundary\nThe blockages are in the layers perpendicular to the short dimension" \
  -define_args {
    {-halo_width "Width of the routing halo" "none" float {required}}
  }




proc report_floating_nets {} {
    global vars
    set out [open RPT/$vars(projectname)/floating_nets.rpt "w"]
    set ss [dbGet [dbGet -p top.nets.numInputTerms 0 ].name]
    foreach dangling $ss {
           puts $out " Dangling Net found :  $dangling "
            puts "Net $dangling "
            #deleteNet $dangling
    }
    close $out
}



proc delete_floating_nets {} {
    global vars
    set out [open RPT/$vars(projectname)/floating_nets.rpt "w"]
    
    set ss [dbGet [dbGet -p top.nets.numInputTerms 0 ].name]
    foreach dangling $ss {
     if {$dangling == "VSS" } {
	} elseif {$dangling == "VDDcore" } {
           } elseif {$dangling == "VDDio" } {
	} else { puts $out " Dangling Net found :  $dangling "
            puts " deleting Net $dangling "
            deleteNet $dangling }
    }
    close $out
}




proc report_floating_instances {} {
    global vars
    set out [open RPT/$vars(projectname)/floating_instances.rpt "w"]
    foreach instPtr [dbGet top.insts] {
          set instName [dbGet $instPtr.name]
          set connectionFound 0
# Foreach instance term check if it is connected to a net. If
# it is connected to a net make sure output terms drive a sink,
# and sinks are driven by output term. Set $connectionFound = 1
# if any connections are found.
 
          foreach instTerm [dbGet $instPtr.instTerms] {
                if {[dbGet $instTerm.net] != "0x0"} {
# If term is an input, check if the net has a driver
                      set isInput [dbGet $instTerm.isInput]
                      set isOutput [dbGet $instTerm.isOutput]
                      set numOutputTerms [dbGet $instTerm.net.numOutputTerms]
                      set numInputTerms [dbGet $instTerm.net.numInputTerms]
                          if {$isInput == "1" && $numOutputTerms > 0} {
                            set connectionFound 1
                          }
                          if {$isOutput == "1" && $numInputTerms > 0} {
                            set connectionFound 1
                          }
                    }
              }
              if {$connectionFound == 0} {
                    puts $out "Instance $instName is floating"
          }
    }
    close $out
}

proc reportDriverHterm {moduleName} {
    set out [open RPT/hierarchy_nets.rpt "w"]
    set instPtr [dbGet -p2 [dbGet -p top.hInst.allTreeInsts.objType hInst].cell.name $moduleName]
     foreach hInstTermsPtr [dbGet -p2 $instPtr.hInstTerms.term.isInput 1] {
              foreach netPtr [dbGet $hInstTermsPtr.net] {
                    foreach outputTerm [dbGet -p $netPtr.allTerms.isOutput 1] {
                     puts "Driver of net [dbGet $netPtr.name] going through hTerm [dbGet $hInstTermsPtr.name] is [dbGet $outputTerm.name]"
                     puts $out "Driver of net [dbGet $netPtr.name] going through hTerm [dbGet $hInstTermsPtr.name] is [dbGet $outputTerm.name]"
                     }
              }
        }
}


proc report_floating_IO_ports {} {
    global vars
    set out [open RPT/$vars(projectname)/floating_io_ports.rpt "w"]
set a [dbGet [dbGet [dbGet top.terms {(.isInput)}].net {.numInputTerms == 0}].name]
set b [dbGet [dbGet [dbGet top.terms {(.isOutput)}].net {.numOutputTerms == 0}].name]
puts $out "list of floating IO ports $a $b"
close $out
}


proc report_all_floating {} {
	report_floating_IO_ports
	report_floating_instances
	report_floating_nets
	}

proc delete_warnings {} {
	set_message -id NRIG-39 -no_limit
	set_message -id LEFPARS-2007 -suppress
	set_message -id IMPLF-201 -suppress
	set_message -id TECHLIB-436 -suppress
	set_message -id TECHLIB-302 -suppress
	set_message -id IMPFP-3961 -suppress
	set_message -id IMPLF-200 -suppress
	set_message -id TECHLIB-1161 -suppress
	set_message -id TECHLIB-1329 -suppress
	set_message -id IMPTS-282 -suppress
	set_message -id TECHLIB-1318 -suppress	
	#set_message -id LEFPARS-2001 -suppress	
	set_message -id IMPLF-58 -suppress
	set_message -no_limit -id TA-113	
}

proc user_delete_floating_latch { latch_name } {
  ## dump instances for sequencial cells  having  floating outputs or no connection at outputs for the supplied  pattern names for cells

  set outfile [open latch_floating.tcl "w"]
  dbForEachCellInst [dbgTopCell] inst_ptr {
    dbForEachInstTerm $inst_ptr term_ptr {
      set cellName [dbObjName  [dbInstCell $inst_ptr]]
      if { [dbIsCellSequential ${cellName}] && [regexp $latch_name  ${cellName}] } {
        if {[dbIsTermUnused $term_ptr] } {
           puts $outfile "##INFO Pin [dbTermName $term_ptr] of given Latch  instance [dbInstName $inst_ptr] is floating for cell name $cellName  "
           puts $outfile "deleteInst  [dbInstName $inst_ptr] "
        }
      }
    }
  }
  Puts "##==> INFO review latch_floating.tcl and source to delete such floating instance \n "
  close $outfile
}


proc findEmptyModule {args} {
  if {[regexp {\-verbose} $args]} { set vflag 1 } else {set vflag 0}
  set hinst [ dbget top.hInst.allTreeInsts]
  foreach inst $hinst {
    if {[dbget $inst.objType] == "hInst"} {
      if {[dbget $inst.allInsts] == 0x0} {
        set instname [dbget $inst.name]
        set modname  [dbget $inst.vCell.name]
        puts "Empty module $modname at instance $instname"
        if {$vflag == 1} {
          set deleteOKFlag 1
          foreach term [dbget $inst.hInstTerms] {
            set termname [trimPath [dbget $term.name]]
            set netptr  [dbget $term.net]
            if {$netptr == 0x0 } {
              puts "Pin $termname -> Net : <no net>"
            } else {
              set deleteOKFlag 0
              set netname [dbget $netptr.name]
              set netterms [dbget $netptr.numTerms]
              puts "Pin $termname -> Net : $netname with $netterms connections"
            }
          }
          if {$deleteOKFlag ==1} {
            puts "Cell has no other connections. Cmd deleteEmptyModule is allowed to delete it.\n"
          } else {
            puts "Cell has at least 1 connection. Cmd deleteEmptyModule is not allowed to delete it.\n"
          }
        } 
      }
    }
  }
}


proc compare_terms {} {
	deselectAll
	selectObject Module sb_0__4__0_
	foreach net [dbGet selected.hInstTerms.upHNet.name] {
		lappend sb_0__4__0__nets $net }

	#puts $sb_0__4__0__nets

	deselectAll
	selectObject Module sb_1__0__0_
	foreach net [dbGet selected.hInstTerms.upHNet.name] {
		lappend sb_1__0__0__nets $net }


	#puts "$sb_0__4__0__nets"
	#puts [lindex $sb_0__4__0__nets 1]
	#foreach net_list [$sb_1__0__0__nets] {lsearch -exact $sb_0__4__0__nets test}
	set net_find [lindex $sb_0__4__0__nets 154]
	lsearch -exact $sb_0__4__0__nets $net_find

	foreach net_list [$sb_1__0__0__nets] {lsearch -exact $sb_0__4__0__nets $net_list}

}

proc write_terms_infile {} {
	deselectAll
	selectObject Module sb_0__4__0_
	foreach net [dbGet selected.hInstTerms.upHNet.name] {
		lappend sb_0__4__0__nets $net }

	deselectAll
	selectObject Module sb_1__0__0_
	foreach net [dbGet selected.hInstTerms.upHNet.name] {
		lappend sb_1__0__0__nets $net }

	set filename "nets.rpt"
	set fileId [open $filename "w"]

	puts -nonewline $fileId $sb_1__0__0__nets
	puts -nonewline $fileId "\n\n\n"
	puts -nonewline $fileId $sb_0__4__0__nets
	close $fileId
}


proc report_fanout {cell} {
	global vars
	set out [open RPT/$vars(projectname)/fanout_cell.rpt w]
	set all_MB_insts [dbGet [dbGet -p2 top.insts.cell.name $cell].name]
	foreach MB_Inst $all_MB_insts {
	  set instPtr [dbGet top.insts.name $MB_Inst -p]
	  set instTermOutPtr [dbGet $instPtr.instTerms.isOutput 1 -p]
	  set instTermOutName [dbGet $instTermOutPtr.name]
	  set fanout [dbGet $instTermOutPtr.net.numInputTerms]
	foreach MB_fanout_inst $instTermOutName {
	  set instTermOutPtr_MB_fanout_inst [dbGet top.insts.instTerms.name $MB_fanout_inst -p]
	  set fanout_MBinst [dbGet $instTermOutPtr_MB_fanout_inst.net.numInputTerms]
	  puts $out "$MB_fanout_inst : $fanout_MBinst"
	}
	}
	close $out
}

