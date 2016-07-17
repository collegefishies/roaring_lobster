module tb_hex_counter;

reg clk;
reg add;
reg sub;
wire [29:0] bin_count;
wire [35:0] hex_count;
reg [3:0] dig_incr;
reg [24:0] time_step;
reg reset;

initial begin
    $from_myhdl(
        clk,
        add,
        sub,
        dig_incr,
        time_step,
        reset
    );
    $to_myhdl(
        bin_count,
        hex_count
    );
end

hex_counter dut(
    clk,
    add,
    sub,
    bin_count,
    hex_count,
    dig_incr,
    time_step,
    reset
);

endmodule
