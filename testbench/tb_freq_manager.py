from myhdl import *
from roaring_lobster.hdl import freq_manager
from icecua.interface	import RamBus
from icecua.hdl      	import rom,ram,bussedram
from icecua.sim      	import clkdriver

period=10

@block
def tb_freq_manager():
	stimulus = []

	clk    	= Signal(False)
	trigger	= Signal(False)
	reset  	= ResetSignal(0,active=1,async=False)

	stimulus.append(clkdriver(clk,period=period))

	typ  	= intbv(0,min=0,max=3.2e9)
	depth	= 128

	freq_rambus = RamBus(typ,depth)
	fstep_rambus = RamBus(typ,depth)
	tstep_rambus = RamBus(typ,depth)
	holdt_rambus = RamBus(typ,depth)

	rambi = []
	@always_comb
	def connect_clocks():
		freq_rambus
		fstep_rambus
		tstep_rambus
		holdt_rambus

	##FOR FUTURE NOTICE,
	
	#we want to pass in the RamBi
	#and connect hex_counter, have
	#flawless reset functionality, 
	#restart the schedule on trigger,
	#even halfway through
	#and automatically cycle through the schedule,
	#it should also have an input port for knowing
	#how long the input schedule is.
	return stimulus