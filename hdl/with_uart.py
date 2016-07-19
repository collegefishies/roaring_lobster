from myhdl import *
from roaring_lobster.hdl import freq_manager
from roaring_lobster.hdl import pts_controller
from icecua.hdl import rom, bussedram, ram, uart
from icecua.interface import RamBus
from icecua import sim
from pyprind import ProgBar #just for funsies.

sim_time=int(1e7)

@block
def with_uart(clk,amphenol,fpga_rx,fpga_tx,trigger,led2,reset):
	N=9
	hex_freq = Signal(intbv(0)[4*N:])
	sched_len = Signal(intbv(0,min=0,max=128))
	# amphenol.driven=True
	modules = []

	led2_l = [Signal(False) for i in range(9)]
	led2_i = ConcatSignal(*reversed(led2_l))

	#define the schedule
	#note that all these variables are the same length
	set_freq   	= Signal(intbv(0,min=0,max=int(3.2e9))) #in 10s of hertz
	freq_step  	= Signal(intbv(0,min=0,max=int(3.2e9))) #in log10 
	time_step  	= Signal(intbv(0,min=0,max=int(3.2e9))) #clock cycles
	hold_time  	= Signal(intbv(0,min=0,max=int(3.2e9))) #clock cycles
	nothing    	= Signal(intbv(0,min=0,max=int(3.2e9)))
	sched_index	= Signal(intbv(0,min=0)[8:])

	#define the reset signal
	# reset = ResetSignal(0,active=1,async=True)

	#define rom-manager handshaking signals
	notclock = Signal(bool(1))
	length_of_signals = len(set_freq)
	ready = Signal(True)
	start = Signal(False)
	done  = Signal(False)
	all_data_received = Signal(False)
	trigger_mask = Signal(False)

	@always_comb
	def trigger_finger():
		trigger_mask.next = trigger and all_data_received

	whichram = Signal(intbv(0)[8:])
	biggestblock_l = [Signal(bool(0)) for i in range(length_of_signals)]
	biggestblock = ConcatSignal(*reversed(biggestblock_l))

	#define manager-dec control signals
	curr_freq   = Signal(intbv(0,min=0,max=int(3.2e9)))
	add,sub,dec_clk = [Signal(bool(0)) for x in range(3)]
	incr = Signal(intbv(0)[N:])

	#ram - fsm state stuff
	t_state = enum(
				'READWHICHRAM',
				'PARSEFORRAM',
				'SENDTORAM'
			)

	state = Signal(t_state.READWHICHRAM)

	#define the uart module and the communications arbiter.
	rx_data = Signal(intbv(0)[8:])
	drdy	= Signal(bool(0))
	
	modules.append(uart(
			clk=clk, 
			rx=fpga_rx,
			tx=fpga_tx,
			reset=reset,
			rx_data=rx_data,
			drdy=drdy,
			baudrate=9600,
			freq_in=12e6
		))

	#depth actually /defines/ the depth of the bussedrams.
	freq_rambus 	= RamBus(typical=intbv(0)[32:],depth=128)
	fstep_rambus	= RamBus(typical=intbv(0)[32:],depth=128)
	tstep_rambus	= RamBus(typical=intbv(0)[32:],depth=128)
	hold_rambus 	= RamBus(typical=intbv(0)[32:],depth=128)

	@always_comb
	def clockinverter():
		''' Just connect the notclock signal for passing into the RAMs  '''
		notclock.next = not clk

	freq_rambus_addr 	= Signal(intbv(0)[8:])
	fstep_rambus_addr	= Signal(intbv(0)[8:])
	tstep_rambus_addr	= Signal(intbv(0)[8:])
	hold_rambus_addr 	= Signal(intbv(0)[8:])

	@always_comb
	def ramwiring():
		''' Connect basic signals of the RAMS: data in and data_out and clock'''
		# biggestblock.next = ConcatSignal(*reversed(biggestblock_l))

		freq_rambus.din.next 	= biggestblock[32:]
		fstep_rambus.din.next	= biggestblock[32:]
		tstep_rambus.din.next	= biggestblock[32:]
		hold_rambus.din.next 	= biggestblock[32:]

		freq_rambus.clk.next 	= notclock
		fstep_rambus.clk.next	= notclock
		tstep_rambus.clk.next	= notclock
		hold_rambus.clk.next 	= notclock

		# freq_rambus.raddr.next 	= sched_index
		# fstep_rambus.raddr.next	= sched_index
		# tstep_rambus.raddr.next	= sched_index
		# hold_rambus.raddr.next 	= sched_index

		freq_rambus.waddr.next 	=	freq_rambus_addr 
		fstep_rambus.waddr.next	=	fstep_rambus_addr
		tstep_rambus.waddr.next	=	tstep_rambus_addr
		hold_rambus.waddr.next 	=	hold_rambus_addr 





	@always_comb
	def determine_sched_len():
		''' Combinatorial logic here to determine
		the schedule length as the smallest amount of data points stuck into the RAMs'''
		if (freq_rambus.length < fstep_rambus.length) and (freq_rambus.length < tstep_rambus.length) and (freq_rambus.length < hold_rambus.length):
			sched_len.next = freq_rambus.length
		elif (tstep_rambus.length < fstep_rambus.length) and (tstep_rambus.length < freq_rambus.length) and (tstep_rambus.length < hold_rambus.length):
			sched_len.next = tstep_rambus.length
		elif (hold_rambus.length < fstep_rambus.length) and (hold_rambus.length < freq_rambus.length) and (hold_rambus.length < tstep_rambus.length):
			sched_len.next = hold_rambus.length
		else:
			sched_len.next = fstep_rambus.length

	freq_man_reset = ResetSignal(0,active=1,async=False)

	@block
	def comms_arbiter():
		''' Finite State Machine for parsing data from the UART
		into the appropriate latch and then writing to the appropriate 
		RAM'''

		delayed_reset1 = ResetSignal(0,active=1,async=False)
		delayed_reset2 = ResetSignal(0,active=1,async=False)

		@always_seq(clk.posedge,reset=None)
		def reset_delayer():
			delayed_reset1.next = reset
			delayed_reset2.next = delayed_reset1

		latch_counter = Signal(intbv(0)[8:])

		drdy_turnedon = Signal(bool(0))
		drdy_old	 = Signal(bool(1))

		@always_seq(clk.posedge,reset=reset)
		def drdy_monitor():
			''' This is a little block for determining whether 
			drdy has transitioned in the last clock cycle.
			It effectively turns the drdy step function into 
			a hat function.
			'''
			freq_man_reset.next = drdy_turnedon
			drdy_old.next = drdy
			if drdy != drdy_old and drdy_old == 0:
				drdy_turnedon.next = 1
			else:
				drdy_turnedon.next = 0

		@always_seq(clk.posedge,reset=delayed_reset2)
		def fsm():
			''' This fsm latches (just after) the dataready positive edge
			signal. The data is guaranteed to be ready then.'''
			if state == t_state.READWHICHRAM and drdy_turnedon:
				freq_rambus.we.next 	= 0
				fstep_rambus.we.next	= 0
				tstep_rambus.we.next	= 0
				hold_rambus.we.next 	= 0
				whichram.next = rx_data
				state.next = t_state.PARSEFORRAM
			elif state == t_state.PARSEFORRAM and drdy_turnedon:
				latch_counter.next = latch_counter + 1
				for i in range(8):
					biggestblock_l[i+8*latch_counter].next  = rx_data[i]
				if latch_counter == 3:
					latch_counter.next = 0
					state.next = t_state.SENDTORAM
			elif state == t_state.SENDTORAM:
				if whichram == 0:
					freq_rambus.we.next = 1
					freq_rambus.length.next =  freq_rambus.length + 1
					freq_rambus_addr.next = freq_rambus_addr + 1
					all_data_received.next = 0
				elif whichram == 1:
					fstep_rambus.we.next = 1
					fstep_rambus.length.next = fstep_rambus.length.next+ 1
					fstep_rambus_addr.next = fstep_rambus_addr + 1
					all_data_received.next = 0
				elif whichram == 2:
					tstep_rambus.we.next = 1
					tstep_rambus.length.next = tstep_rambus.length + 1
					tstep_rambus_addr.next = tstep_rambus_addr + 1
					all_data_received.next = 0
				elif whichram == 3:
					hold_rambus.we.next = 1
					hold_rambus.length.next = hold_rambus.length + 1
					hold_rambus_addr.next = hold_rambus_addr + 1
					all_data_received.next = 0
				elif whichram == 22:
					freq_rambus.we.next 	= 0
					fstep_rambus.we.next	= 0
					tstep_rambus.we.next	= 0
					hold_rambus.we.next 	= 0
					all_data_received.next  = 1
				else:
					freq_rambus.we.next 	= 0
					fstep_rambus.we.next	= 0
					tstep_rambus.we.next	= 0
					hold_rambus.we.next 	= 0
				state.next = t_state.READWHICHRAM
			else:
				freq_rambus.we.next 	= 0
				fstep_rambus.we.next	= 0
				tstep_rambus.we.next	= 0
				hold_rambus.we.next 	= 0
		return fsm,drdy_monitor,reset_delayer

	manager = freq_manager(
			clk=clk, reset=freq_man_reset,
			hex_freq=hex_freq,
			freq_rambus=freq_rambus,
			fstep_rambus=fstep_rambus,
			tstep_rambus=tstep_rambus,
			holdt_rambus=hold_rambus,
			sched_length=sched_len,
			trigger=trigger_mask
		)


	pts_connections = pts_controller(
			hex_freq=hex_freq,
			pts_enable=True,
			amphenol=amphenol
		)

	@always_comb
	def led_wiring():
		for i in range(9):
			led2.next = led2_i

		led2_l[8].next = all_data_received
		for i in range(8):
			led2_l[i].next = whichram[i]

	return manager,modules,comms_arbiter(),clockinverter,determine_sched_len,ramwiring,trigger_finger,led_wiring,pts_connections

reset = ResetSignal(1,active=0,async=False)
clk = Signal(bool(0))
amphenol = Signal(intbv(0)[50:])
fpga_rx	= Signal(bool(0))
fpga_tx	= Signal(bool(0))	
trigger = Signal(bool(0))
led2 = Signal(intbv(0)[9:])
inst = with_uart(clk=clk,amphenol=amphenol,fpga_rx=fpga_rx,fpga_tx=fpga_tx,trigger=trigger,led2=led2,reset=reset)
# inst.convert()
# inst.config_sim(trace=True)
# inst.run_sim(sim_time)
