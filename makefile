PYCC=pypy

VPATH=./hdl:./testbench:./build

all: hex_counter.py tb_hex_counter.py

hex_counter.py: build_hex_counter.py 
	cd ./build/ && $(PYCC) build_hex_counter.py

tb_hex_counter.py: hex_counter.py
	$(PYCC) ./testbench/tb_hex_counter.py

clean:
	rm -f *.vcd*
	rm -f *.pyc
	rm -f ./build/*.pyc
	rm -f ./hdl/*.pyc
	rm -f ./testbench/*.pyc