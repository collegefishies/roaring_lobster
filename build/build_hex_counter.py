from myhdl import *
from roaring_lobster.hdl	import hex_counter

N=9

reset    	= ResetSignal(0, active=1,async=False)
clk      	= Signal(False)
add      	= Signal(False)
sub      	= Signal(False)
bin_count	= Signal(intbv(0,min=0,max=10**N))
hex_count	= Signal(intbv(0)[4*N:])
dig_incr 	= Signal(intbv(0,min=0,max=N))
time_step	= Signal(intbv(0)[25:])
N        	= N

inst = hex_counter(
	reset=reset,    
	clk=clk,      
	add=add,      
	sub=sub,      
	bin_count=bin_count,
	hex_count=hex_count,
	dig_incr=dig_incr, 
	time_step=time_step,
	# N=N
	)

inst.convert(hdl='verilog')


inst = hex_counter(
	reset=reset,    
	clk=clk,      
	add=add,      
	sub=sub,      
	bin_count=bin_count,
	hex_count=hex_count,
	dig_incr=dig_incr, 
	time_step=time_step,
	# N=N
	)

inst.convert(hdl='VHDL')