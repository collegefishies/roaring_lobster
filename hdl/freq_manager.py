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

	@always_comb
	def ram_read_signals():
		freq_rambus.raddr.next 	= sched_addr
		fstep_rambus.raddr.next	= sched_addr
		tstep_rambus.raddr.next	= sched_addr
		holdt_rambus.raddr.next	= sched_addr

	sched = enum('START','INCREMENTING','HOLDING','FINISHED')
	hold_counter = Signal(intbv(0)[32:])
	@always_seq(clk.posedge,reset)
	def schedule_stepper():
		if state == sched.START:
			sched_addr.next     	= 0
			dig_incr_offset.next	= 0
			add.next            	= 0
			sub.next            	= 0
			hold_counter.next   	= 0
			if trigger == 1:
				state.next = sched.INCREMENTING
		elif state == sched.INCREMENTING:
			if   bin_count < freq_rambus.dout:
				add.next	= 1
				sub.next	= 0
				if sub == 1:
					dig_incr_offset.next = dig_incr_offset + 1
			elif bin_count > freq_rambus.dout:
				add.next	= 0
				sub.next	= 1
				if add == 1:
					dig_incr_offset.next = dig_incr_offset + 1
			else:
				add.next  	= 0
				sub.next  	= 0
				state.next	= sched.HOLDING
		elif state == sched.HOLDING:
			hold_counter.next = hold_counter + 1
			
			if hold_counter == holdt_rambus.dout:
				sched_addr.next = sched_addr + 1
				if sched_addr == sched_length - 1:
					state.next = sched.FINISHED
				else:
					state.next = sched.INCREMENTING
		elif state == sched.FINISHED:
			hold_counter.next = 0
			state.next = sched.FINISHED

	return hex_counter_instance,digit_to_increment,ram_read_signals,schedule_stepper
