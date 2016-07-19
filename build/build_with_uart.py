from myhdl import *
from roaring_lobster.hdl import with_uart


clk = Signal(False)
amphenol = Signal(intbv(0)[50:])
fpga_rx,fpga_tx = [Signal(False), Signal(False)]
trigger  = Signal(False)
led2	= Signal(intbv(0)[9:])
reset = ResetSignal(1,active=0,async=False)

print "WARNING!: The reset pin for with_uart.v/with_uart.vhd is ACTIVE LOW!!!!"
print "WARNING!: The reset pin for with_uart.v/with_uart.vhd is ACTIVE LOW!!!!"
print "WARNING!: The reset pin for with_uart.v/with_uart.vhd is ACTIVE LOW!!!!"

inst = with_uart(clk,amphenol,fpga_rx,fpga_tx,trigger,led2,reset)
inst.convert(hdl='verilog')
inst = with_uart(clk,amphenol,fpga_rx,fpga_tx,trigger,led2,reset)
inst.convert(hdl='VHDL')
