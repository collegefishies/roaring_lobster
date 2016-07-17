from myhdl import *
from icecua.hdl import rom

@block
def hex_counter(
	clk,
	add, sub,
	bin_count, hex_count, 
	dig_incr,
	time_step,
	reset,
	N):
	''' A counter module with two outputs, hex_count, bin_count, each being 
	the 'decimal' in hexadecimal representation, and the other being
	the binary representation. dig_incr is the module that determines by
	what power of ten to increment by, i.e., hex_count.next = hex_count + 
	10**dig_incr.
	add, and sub are clock enables that determine whether we should add
	or subtract.
	'''

	#whether or not we need to subtract/add a certain digit
	to_subtract	= [Signal(False) for i in range(N)]
	to_add     	= [Signal(False) for i in range(N)]

	#decomposition of the binary number we're working with
	hex_l    	= [Signal( intbv(0,min=0,max=10) ) for i in downrange(N)]
	hex_int  	= ConcatSignal(*reversed(hex_l))
	bin_int  	= Signal(intbv(0,min=-10**N,max=10**N))
	# bin_int	= Signal(intbv(0))

	int_clk   	= Signal(False)
	clk_p_time	= Signal(False)
	
	@always_comb
	def wiring():
		hex_count.next = hex_int
		bin_count.next = bin_int
		if time_step == 0 or time_step == 1:
			int_clk.next = clk
		else:
			int_clk.next = clk_p_time

	clk_counter = Signal(intbv(0)[32:])
	@always_seq(clk.posedge,reset)
	def clk_driver():
		''' Drives a pulse with period,
		time_step. '''
		if clk_counter == 0:
			clk_p_time.next = 1
			clk_counter.next = clk_counter + 1
		elif clk_counter >= time_step - 1:
			clk_p_time.next = 0
			clk_counter.next = 0
		else:
			clk_p_time.next = 0
			clk_counter.next = clk_counter + 1

	@always(dig_incr,*(hex_l + to_add + to_subtract))
	def addsublogic():
		''' This module determines whether or not to add/sub certain bits,
		in the case of carry over. First we make sure we don't add/sub all
		the bits lower than increment, then we set the increment bit to add/sub,
		and lastly we perform the logic neccessary to determine if bits greater
		than dig_incr need to be added

		It's sensitivity list is long, this is neccessary as to allow the logic 
		to update to_add when any part of to_add changes, as is the case
		when performing carry logic.
		'''
		for digit in range(N):
			if digit < dig_incr:
				to_add[digit].next = 0
				to_subtract[digit].next = 0
			elif digit == dig_incr:
				to_add[dig_incr].next = 1
				to_subtract[dig_incr].next = 1
			else:
				to_add[digit].next     	= (hex_l[digit-1] == 9) and to_add[digit-1]
				to_subtract[digit].next	= (hex_l[digit-1] == 0) and to_subtract[digit-1]

	@always_seq(int_clk.negedge, reset=reset)
	def counter():
		''' This is the hexadecimal and binary counter.
		It adds or subtracts only if (add xor sub) is True, to allow for the carry logic
		a new bit of logic is required, namely addlogic, and sublogic. They give out 
		lists of vectors (or integer masks). These are used in the logic below. And work 
		out most of the stuff. One extra if statement is needed to increment the desired 
		byte.
		'''

		#bin counter with wrap around control.
		if (bin_int + increment > 10**N - 1) and (add == True and sub == False):
			bin_int.next = bin_int + increment - 10**N
		elif (bin_int < increment) and (sub == True and add == False):
			bin_int.next = bin_int - increment + 10**N
		else:
			if add == True and sub == False:
				bin_int.next = bin_int + increment
			elif sub == True and add == False:
				bin_int.next = bin_int - increment
			else:
				bin_int.next = bin_int

		#hex counter
		if add == True and (not sub):
			for digit in range(0,N):
				if digit > dig_incr:
					if to_add[digit]:
						if hex_l[digit] != 9:
							hex_l[digit].next = hex_l[digit] + 1
						else:
							hex_l[digit].next = 0
					else:
						hex_l[digit].next = hex_l[digit]
				elif digit == dig_incr:
					if hex_l[dig_incr] != 9:
						hex_l[dig_incr].next = hex_l[dig_incr] + 1
					else:
						hex_l[dig_incr].next = 0
		elif sub == True and (not add):
			for digit in range(0,N):
				if digit > dig_incr:
					if to_subtract[digit]:
						if hex_l[digit] != 0:
							hex_l[digit].next = hex_l[digit] - 1
						else:
							hex_l[digit].next = 9
					else:
						hex_l[digit].next = hex_l[digit]
				elif digit == dig_incr:
					if hex_l[dig_incr] != 0:
						hex_l[dig_incr].next = hex_l[dig_incr] - 1
					else:
						hex_l[dig_incr].next = 9
		else:
			for digit in range(N):
				hex_l[digit].next = hex_l[digit]

	increment = Signal(intbv(0,min=0,max=10**N + 1))
	increment_amounts = tuple([10**i for i in range(N)])
	rom_inst = rom(dout=increment,addr=dig_incr,CONTENT=increment_amounts)

	return wiring,counter,addsublogic,rom_inst,clk_driver