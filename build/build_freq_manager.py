from myhdl import *
from icecua.interface import RamBus
from roaring_lobster.hdl import freq_manager

N = 9
typ  	= intbv(0,min=0,max=3.2e9)
depth	= 128

clk         	= Signal(False)
trigger     	= Signal(False)
reset       	= ResetSignal(0,active=1,async=False)
sched_length	= Signal(intbv(0,min=0,max=depth))


hex_freq	= Signal(intbv(0)[4*N:])

freq_rambus = RamBus(typ,depth)
fstep_rambus = RamBus(typ,depth)
tstep_rambus = RamBus(typ,depth)
holdt_rambus = RamBus(typ,depth)


inst = freq_manager(
			clk, reset,
			hex_freq,
			freq_rambus,
			fstep_rambus,
			tstep_rambus,
			holdt_rambus,
			sched_length,
			trigger
		)
inst.convert(hdl='verilog')

inst = freq_manager(
			clk, reset,
			hex_freq,
			freq_rambus,
			fstep_rambus,
			tstep_rambus,
			holdt_rambus,
			sched_length,
			trigger
		)
inst.convert(hdl='VHDL')