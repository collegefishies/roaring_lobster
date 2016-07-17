from myhdl import *
from roaring_lobster.hdl import freq_manager, hex_counter
from icecua.interface	import RamBus
from icecua.hdl      	import rom,ram,bussedram
from icecua.sim      	import clkdriver

period=10
N=9

@block
def freq_manager(
			clk, reset,
			hex_freq,
			freq_rambus,
			fstep_rambus,
			tstep_rambus,
			holdt_rambus,
			sched_length,
			trigger
		):

	#we want to pass in the RamBi
	#and connect hex_counter, have
	#flawless reset functionality, 
	#restart the schedule on trigger,
	#even halfway through
	#and automatically cycle through the schedule,
	#it should also have an input port for knowing
	#how long the input schedule is.

	sched_addr = Signal(intbv(0,min=0,max=128))

	add, sub  = [Signal(False) for _ in range(2)]
	bin_count = Signal(intbv(0,min=0,max=10**N))
	hex_count = Signal(intbv(0)[4*N:])
	dig_incr  = Signal(intbv(0,min=0,max=N))
	hex_counter_instance = hex_counter(
			clk=clk, add=add, sub=sub,
			bin_count=bin_count,
			hex_count=hex_count,
			dig_incr=dig_incr,
			time_step=tstep_rambus.dout,
			reset=reset, N=N
		)

	@always_comb
	def digit_to_increment():
		''' Connect the ram fstep with 
		a value we subtract for allowing for convergence'''
		dig_incr.next = fstep_rambus.dout - dig_incr_offset

	@always_seq(clk.posedge,reset)
	def schedule_stepper():
		if state == sched.START:
			sched_addr.next     	= 0
			dig_incr_offset.next	= 0
			add.next            	= 0
			sub.next            	= 0
			if trigger == 1:
				state.next = sched.INCREMENTING
		elif state == sched.INCREMENTING:

		elif state == sched.HOLDING:


			if sched_addr == sched_length:
				state.next = sched.FINISHED
			else:
				state.next = sched.INCREMENTING
		elif state == sched.FINISHED:

			state.next = sched.FINISHED

	return hex_counter_instance,digit_to_increment,schedule_stepper
