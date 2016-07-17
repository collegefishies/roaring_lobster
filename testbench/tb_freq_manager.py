from myhdl import *
from roaring_lobster.hdl import freq_manager
from icecua.interface	import RamBus
from icecua.hdl      	import rom,ram,bussedram
from icecua.sim      	import clkdriver

period=10

@block
def tb_freq_manager():
	clk    	= Signal(False)
	trigger	= Signal(False)
	reset  	= ResetSignal(0,active=1,async=False)

	typ  	= intbv(0,min=0,max=3.2e9)
	depth	= 128

	freq_rambus = RamBus(typ,depth)
	fstep_rambus = RamBus(typ,depth)
	tstep_rambus = RamBus(typ,depth)
	holdt_rambus = RamBus(typ,depth)

	addr	= Signal(intbv(0,min=0,max=depth))
	din 	= Signal(typ)
	we  	= Signal(False)

	@always_comb
	def connect_rams():
		''' Connect the write ports,
		and the clocks here.'''
		freq_rambus.clk.next  	= clk
		fstep_rambus.clk.next 	= clk
		tstep_rambus.clk.next 	= clk
		holdt_rambus.clk.next 	= clk
		freq_rambus.din.next  	= din
		fstep_rambus.din.next 	= din
		tstep_rambus.din.next 	= din
		holdt_rambus.din.next 	= din
		freq_rambus.addr.next 	= addr
		fstep_rambus.addr.next	= addr
		tstep_rambus.addr.next	= addr
		holdt_rambus.addr.next	= addr
		freq_rambus.we.next   	= we
		fstep_rambus.we.next  	= we
		tstep_rambus.we.next  	= we
		holdt_rambus.we.next  	= we

	uut = freq_manager(
			clk=clk, reset=reset,
			freq_rambus=freq_rambus,
			fstep_rambus=tstep_rambus,
			tstep_rambus=tstep_rambus,
			holdt_rambus=holdt_rambus,
			sched_length=schedule_length,
			trigger=trigger
		)

	#we want to pass in the RamBi
	#and connect hex_counter, have
	#flawless reset functionality, 
	#restart the schedule on trigger,
	#even halfway through
	#and automatically cycle through the schedule,
	#it should also have an input port for knowing
	#how long the input schedule is.
	
	freq = [0, 25400000.0, 30000000.0, 29000000.0, 10000000.0, 20000000.0]
	fstep= [6, 1, 0, 0, 7, -1]
	tstep= [1, 1, 1, 1, 37502813, -1]
	holdt= [0, 0, 0, 0, 0, -1]
	@instance
	def stimulus():
		yield(500)
		for i in range(sched_length):
			addr.next = 0
			din.next = int(freq[i])
			yield delay(30)

			yield delay(20)

	return uut, stimulus,clkdriver(clk,period=period)
