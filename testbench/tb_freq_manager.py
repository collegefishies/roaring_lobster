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

	freq_t= (20000000	, 25400000	, 30000000	, 29000000	, 10000000	, 20000000)
	fstep_t= (6      	, 7       	, 5       	, 5       	, 6       	, 6)
	tstep_t= (1      	, 1       	, 1       	, 1       	, 5       	, 3)
	holdt_t= (100    	, 100     	, 100     	, 100     	, 100     	, 100)

	freq 	= Signal(intbv(0,min=0,max=3.2e9))
	fstep	= Signal(intbv(0,min=0,max=3.2e9))
	tstep	= Signal(intbv(0,min=0,max=3.2e9))
	holdt	= Signal(intbv(0,min=0,max=3.2e9))

	rom_addr = Signal(intbv(0,min=0,max=depth))
	roms = [
		rom(freq,rom_addr,freq_t),
		rom(fstep,rom_addr,fstep_t),
		rom(tstep,rom_addr,tstep_t),
		rom(holdt,rom_addr,holdt_t)
	]
	schedule_length = len(freq_t)
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
		reset.next = 0
		addr.next = 0
		rom_addr.next = 0
		we.next = 0
		trigger.next = 0
		freq_rambus.din.next =  0
		fstep_rambus.din.next = 0
		tstep_rambus.din.next = 0
		holdt_rambus.din.next = 0
		yield delay(30)
		reset.next = 1

		yield delay(30)
		reset.next = 0

		yield delay(500)
		for i in range(len(freq_t)):
			rom_addr.next = i
			addr.next = i
			freq_rambus.din.next =  int(freq)
			fstep_rambus.din.next = int(fstep)
			tstep_rambus.din.next = int(tstep)
			holdt_rambus.din.next = int(holdt)
			yield delay(20)
			we.next = 1
			yield delay(20)
			we.next = 0

		yield delay(50)
		reset.next = 1 
		yield delay(50)
		reset.next = 0
		yield delay(20)
		trigger.next = 1
		yield delay(100)
		trigger.next = 0
		yield delay(10000)
		trigger.next = 1
		yield delay(50)
		# trigger.next = 0
		yield delay(400000)
		trigger.next = 1
		yield delay(50)
		# trigger.next = 0
	return uut, stimulus,clkdriver(clk,period=period), connect_rams,roms

inst = tb_freq_manager()
inst.config_sim(trace=True)
inst.run_sim(5e5)
inst = tb_freq_manager()
inst.convert(hdl='verilog')
inst = tb_freq_manager()
inst.convert(hdl='VHDL')
