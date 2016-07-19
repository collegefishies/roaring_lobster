module tb_freq_manager;

reg clk;
reg reset;
wire [35:0] hex_freq;
reg [6:0] sched_length;
reg trigger;
reg freq_rambus_clk;
reg bussedram_4_rambus_we;
reg [6:0] bussedram_4_rambus_waddr;
wire [6:0] freq_rambus_raddr;
reg [31:0] bussedram_4_rambus_din;
wire [31:0] freq_rambus_dout;
reg [6:0] freq_rambus_length;
reg fstep_rambus_clk;
reg bussedram_5_rambus_we;
reg [6:0] bussedram_5_rambus_waddr;
wire [6:0] fstep_rambus_raddr;
reg [31:0] bussedram_5_rambus_din;
wire [31:0] fstep_rambus_dout;
reg [6:0] fstep_rambus_length;
reg tstep_rambus_clk;
reg bussedram_6_rambus_we;
reg [6:0] bussedram_6_rambus_waddr;
wire [6:0] tstep_rambus_raddr;
reg [31:0] bussedram_6_rambus_din;
wire [31:0] hex_counter_1_time_step;
reg [6:0] tstep_rambus_length;
reg holdt_rambus_clk;
reg bussedram_7_rambus_we;
reg [6:0] bussedram_7_rambus_waddr;
wire [6:0] holdt_rambus_raddr;
reg [31:0] bussedram_7_rambus_din;
wire [31:0] holdt_rambus_dout;
reg [6:0] holdt_rambus_length;

initial begin
    $from_myhdl(
        clk,
        reset,
        sched_length,
        trigger,
        freq_rambus_clk,
        bussedram_4_rambus_we,
        bussedram_4_rambus_waddr,
        bussedram_4_rambus_din,
        freq_rambus_length,
        fstep_rambus_clk,
        bussedram_5_rambus_we,
        bussedram_5_rambus_waddr,
        bussedram_5_rambus_din,
        fstep_rambus_length,
        tstep_rambus_clk,
        bussedram_6_rambus_we,
        bussedram_6_rambus_waddr,
        bussedram_6_rambus_din,
        tstep_rambus_length,
        holdt_rambus_clk,
        bussedram_7_rambus_we,
        bussedram_7_rambus_waddr,
        bussedram_7_rambus_din,
        holdt_rambus_length
    );
    $to_myhdl(
        hex_freq,
        freq_rambus_raddr,
        freq_rambus_dout,
        fstep_rambus_raddr,
        fstep_rambus_dout,
        tstep_rambus_raddr,
        hex_counter_1_time_step,
        holdt_rambus_raddr,
        holdt_rambus_dout
    );
end

freq_manager dut(
    clk,
    reset,
    hex_freq,
    sched_length,
    trigger,
    freq_rambus_clk,
    bussedram_4_rambus_we,
    bussedram_4_rambus_waddr,
    freq_rambus_raddr,
    bussedram_4_rambus_din,
    freq_rambus_dout,
    freq_rambus_length,
    fstep_rambus_clk,
    bussedram_5_rambus_we,
    bussedram_5_rambus_waddr,
    fstep_rambus_raddr,
    bussedram_5_rambus_din,
    fstep_rambus_dout,
    fstep_rambus_length,
    tstep_rambus_clk,
    bussedram_6_rambus_we,
    bussedram_6_rambus_waddr,
    tstep_rambus_raddr,
    bussedram_6_rambus_din,
    hex_counter_1_time_step,
    tstep_rambus_length,
    holdt_rambus_clk,
    bussedram_7_rambus_we,
    bussedram_7_rambus_waddr,
    holdt_rambus_raddr,
    bussedram_7_rambus_din,
    holdt_rambus_dout,
    holdt_rambus_length
);

endmodule
