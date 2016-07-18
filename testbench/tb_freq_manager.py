from myhdl import *
from roaring_lobster.hdl import freq_manager
from icecua.interface	import RamBus
from icecua.hdl      	import rom,ram,bussedram
from icecua.sim      	import clkdriver

period=10
N=9

@block
def tb_freq_manager():
	clk    	= Signal(False)
	trigger	= Signal(False)
	reset  	= ResetSignal(0,active=1,async=False)

	typ  	= intbv(0,min=0,max=3.2e9)
	depth	= 128

	hex_freq	= Signal(intbv(0)[4*N:])
	
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
		freq_rambus.clk.next 	= clk
		fstep_rambus.clk.next	= clk
		tstep_rambus.clk.next	= clk
		holdt_rambus.clk.next	= clk

		freq_rambus.waddr.next 	= addr
		fstep_rambus.waddr.next	= addr
		tstep_rambus.waddr.next	= addr
		holdt_rambus.waddr.next	= addr
		freq_rambus.we.next    	= we
		fstep_rambus.we.next   	= we
		tstep_rambus.we.next   	= we
		holdt_rambus.we.next   	= we

	freq = [0, 25400000.0, 30000000.0, 29000000.0, 10000000.0, 20000000.0]
	fstep= [6, 7, 4, 4, 6, 3]
	tstep= [1, 1, 1, 1, 5, 3]
	holdt= [100, 100, 100, 100, 100, 100]
	schedule_length = len(freq)
	# schedule_length = 3

	uut = freq_manager(
			clk=clk, reset=reset,
			hex_freq=hex_freq,
			freq_rambus=freq_rambus,
			fstep_rambus=fstep_rambus,
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
	#and automatically cycle through the sche1dule,
	#it should also have an input port for knowing
	#how long the input schedule is.
	
	@instance
	def stimulus():
		yield delay(500)
		for i in range(len(freq)):
			addr.next = i
			freq_rambus.din.next =  int(freq[i])
			fstep_rambus.din.next = int(fstep[i])
			tstep_rambus.din.next = int(tstep[i])
			holdt_rambus.din.next = int(holdt[i])
			yield delay(20)
			we.next = 1
			yield delay(20)
			we.next = 0

		yield delay(20)
		trigger.next = 1
		yield delay(100)
		trigger.next = 0
		yield delay(10000)
		trigger.next = 1
		yield delay(50)
		trigger.next = 0
		yield delay(400000)
		trigger.next = 1
		yield delay(50)
		trigger.next = 0
	return uut, stimulus,clkdriver(clk,period=period), connect_rams

inst = tb_freq_manager()
inst.config_sim(trace=True)
inst.run_sim(1e8)
inst = tb_freq_manager()
inst.convert(hdl='verilog')
inst = tb_freq_manager()
inst.convert(hdl='VHDL')
