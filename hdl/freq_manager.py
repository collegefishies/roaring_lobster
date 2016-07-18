from myhdl import *
from roaring_lobster.hdl import hex_counter
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

	add, sub       	= [Signal(False) for _ in range(2)]
	bin_count      	= Signal(intbv(0,min=-10**N+1,max=10**N+1))
	hex_count      	= Signal(intbv(0)[4*N:])
	dig_incr       	= Signal(intbv(0,min=0,max=N))
	dig_incr_offset	= Signal(intbv(0,min=0,max=N))

	hex_counter_instance = hex_counter(
			clk=clk, add=add, sub=sub,
			bin_count=bin_count,
			hex_count=hex_count,
			dig_incr=dig_incr,
			time_step=tstep_rambus.dout,
			reset=reset, N=N
		)

	@always_comb
	def wiring():
		hex_freq.next = hex_count

	@always_comb
	def digit_to_increment():
		''' Connect the ram fstep with 
		a value we subtract for allowing for convergence'''
		if fstep_rambus.dout >= dig_incr_offset:
			dig_incr.next = fstep_rambus.dout - dig_incr_offset
		else:
			dig_incr.next = 0

	@always_comb
	def ram_read_signals():
		# freq_rambus.clk.next 	= clk
		# fstep_rambus.clk.next	= clk
		# tstep_rambus.clk.next	= clk
		# holdt_rambus.clk.next	= clk

		freq_rambus.raddr.next 	= sched_addr
		fstep_rambus.raddr.next	= sched_addr
		tstep_rambus.raddr.next	= sched_addr
		holdt_rambus.raddr.next	= sched_addr

	sched = enum('START','INCREMENTING','HOLDING','FINISHED')
	state = Signal(sched.START)
	hold_counter = Signal(intbv(0)[32:])
	incr_amount = Signal(intbv(0,min=0,max=10**N))
	@always_seq(clk.negedge,reset)
	def schedule_stepper():
		if state == sched.START:
			sched_addr.next     	= 0
			dig_incr_offset.next	= 0
			add.next            	= 0
			sub.next            	= 0
			hold_counter.next   	= 0
			if trigger == 1:
				state.next = sched.INCREMENTING
			else:
				state.next = sched.START
		elif state == sched.INCREMENTING:
			hold_counter.next = 0
			if bin_count == freq_rambus.dout:
				add.next = 0
				sub.next = 0
				state.next = sched.HOLDING
			elif bin_count < freq_rambus.dout and add == 0 and sub == 0:
				add.next = 1
				sub.next = 0
				dig_incr_offset.next = 0
			elif bin_count > freq_rambus.dout and add == 0 and sub == 0:
				add.next = 0
				sub.next = 1
				dig_incr_offset.next = 0
			elif bin_count < freq_rambus.dout and add == 1 and sub == 0:
				if bin_count + incr_amount > freq_rambus.dout:
					add.next = 0
					sub.next = 1
					dig_incr_offset.next = dig_incr_offset + 1
				elif bin_count + incr_amount == freq_rambus.dout:
					add.next = 0 
					sub.next = 0
					state.next = sched.HOLDING
				else:
					add.next = 1
					sub.next = 0
			elif bin_count < freq_rambus.dout and add == 0 and sub == 1:
				add.next = 1
				sub.next = 0
			elif bin_count > freq_rambus.dout and add == 0 and sub == 1:
				if bin_count < freq_rambus.dout + incr_amount:
					add.next = 1
					sub.next = 0
					dig_incr_offset.next = dig_incr_offset + 1
				elif bin_count == freq_rambus.dout + incr_amount:
					add.next = 0
					sub.next = 0
					state.next = sched.HOLDING
				else:
					add.next = 0
					sub.next = 1
			else: #bin_count > freq_rambus.dout and add == 1 and sub == 0
			      sub.next = 1
			      add.next = 0
		elif state == sched.HOLDING:
			if hold_counter >= holdt_rambus.dout:
				sched_addr.next = sched_addr + 1
				hold_counter.next = 0
				if sched_addr == sched_length - 1:
					state.next = sched.FINISHED
				else:
					state.next = sched.INCREMENTING
			else:
				hold_counter.next = hold_counter + 1
		else: # state == sched.FINISHED:
			sched_addr.next     	= 0
			dig_incr_offset.next	= 0
			add.next            	= 0
			sub.next            	= 0
			hold_counter.next   	= 0
			state.next = sched.FINISHED
			if trigger == 1:
				state.next = sched.START

	rams = []

	rams.append(bussedram(freq_rambus))
	rams.append(bussedram(fstep_rambus))
	rams.append(bussedram(tstep_rambus))
	rams.append(bussedram(holdt_rambus))

	rams.append(rom(dout=incr_amount,addr=dig_incr,CONTENT=tuple([10**i for i in range(N)])))

	return hex_counter_instance,digit_to_increment,ram_read_signals,schedule_stepper,rams,wiring
