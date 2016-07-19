module tb_with_uart;

reg clk;
wire [49:0] amphenol;
reg fpga_rx;
reg fpga_tx;
reg trigger;
wire [8:0] led2;
reg reset;

initial begin
    $from_myhdl(
        clk,
        fpga_rx,
        fpga_tx,
        trigger,
        reset
    );
    $to_myhdl(
        amphenol,
        led2
    );
end

with_uart dut(
    clk,
    amphenol,
    fpga_rx,
    fpga_tx,
    trigger,
    led2,
    reset
);

endmodule
