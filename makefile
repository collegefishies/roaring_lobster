PYCC=pypy

VPATH=./hdl:./testbench:./build

all: hex_counter.py freq_manager.py with_uart.py

with_uart.py: freq_manager.py hex_counter.py
	cd ./build/ && $(PYCC) build_with_uart.py

freq_manager.py: build_freq_manager.py hex_counter.py
	cd ./build/ && $(PYCC) build_freq_manager.py

hex_counter.py: build_hex_counter.py 
	cd ./build/ && $(PYCC) build_hex_counter.py

tb_top.py: with_uart.py
	cd ./simulation && $(PYCC) ../testbench/tb_top.py

tb_freq_manager.py: freq_manager.py hex_counter.py
	cd ./simulation && $(PYCC) ../testbench/tb_freq_manager.py

tb_hex_counter.py: hex_counter.py
	cd ./simulation && $(PYCC) ../testbench/tb_hex_counter.py

clean:
	rm -f *.vcd*
	rm -f ./build/*.vcd*
	rm -f *.pyc
	rm -f ./build/*.pyc
	rm -f ./pytools/*.pyc
	rm -f ./hdl/*.pyc
	rm -f ./testbench/*.pyc
