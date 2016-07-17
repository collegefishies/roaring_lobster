from myhdl import *
from roaring_lobster.hdl	import hex_counter
from icecua.sim         	import clkdriver
@block
def tb_hex_counter():
	N = 10

	clk = Signal(False)

	add = Signal(False)
	sub = Signal(False)

	#on reset, hex_count, bin_count should reset to zero
	#and the internal clock (dictated by time_step) should
	#reset.
	reset = ResetSignal(0, active=1, async = True)

	dig_incr  = Signal(intbv(0,min=0,max=N))
	time_step = Signal(intbv(0)[32:])

	hex_count = Signal(intbv(0)[4*N:])
	bin_count = Signal(intbv(0,min=0,max=10**N))

	clock_driver = clkdriver(clk=clk, period=10)

	uut = hex_counter(
			clk=clk,
			add=add,
			sub=sub,
			reset=reset,
			dig_incr=dig_incr,
			time_step=time_step,
			hex_count=hex_count,
			bin_count=bin_count,
			N=N
		)

	@instance
	def stimulus():
		pass
		yield delay(500)

		add.next = 1
		sub.next = 0

		yield delay(100)

		#drive all the digits.
		#This should wrap around on
		#being overdriven, both in binary 
		#and hex
		for i in range(N):
			dig_incr.next = i
			yield delay(100)


		add.next = 0
		sub.next = 1

		yield delay(100)

		for i in downrange(N):
			dig_incr.next = i
			yield delay(100)

		yield delay(100)

		add.next = 0
		sub.next = 0

		yield delay(10)
		print "We should be zero here,"
		print "Actually we have	(hex): %s" % hex(hex_count.val)
		print "                	(bin): %s" %     bin_count.val

		yield delay(100)
		
		reset.next = 1
		yield delay(10)
		print "Changing timestep to 50."

		time_step.next = 50
		dig_incr.next = 0

		add.next = 1
		sub.next = 0
		yield delay(10)
		reset.next = 0
		yield delay(5000)

		print "We should be at 10, we're actually at %d" % bin_count
		print "In hex: %s" % hex(hex_count)

		for i in range(N):
			dig_incr.next = i
			yield delay(5000)

		add.next = 0
		sub.next = 0

	return uut, stimulus, clock_driver

inst = tb_hex_counter()
inst.config_sim(trace=True)
inst.run_sim(1000000)