PYCC=pypy

VPATH=../hdl

tb_hex_counter.py: hex_counter.py
	$(PYCC) tb_hex_counter.py
	# gtkwave --cpu=4 tb_hex_counter.vcd

clean:
	rm *.vcd*

