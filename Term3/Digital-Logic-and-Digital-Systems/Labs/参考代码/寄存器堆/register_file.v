module register_file(clk, clr, Din, CRW, A_write, A_read, en_decode, en_tri, Dout);
    input wire clk;
    input wire clr;
    input wire [7:0] Din;
    input wire CRW;
    input wire [1:0] A_write;
    input wire [1:0] A_read;
    input wire en_decode;
    input wire en_tri;
    
    output wire [7:0] Dout;

    wire [3:0] en2reg;
    wire [7:0] reg_data1, reg_data2, reg_data3, reg_data4;

    decode2_4 decode2_4 (
        .A(A_write),
        .en_decode(en_decode),
        .Y(en2reg)
    );
	
	register_8 register1 (
					.clk(clk),
					.clr(clr),
					.en(en2reg[0]),
					.CRW(CRW),
					.D(Din),
					.Q(reg_data1)
				);
	
	register_8 register2 (
					.clk(clk),
					.clr(clr),
					.en(en2reg[1]),
					.CRW(CRW),
					.D(Din),
					.Q(reg_data2)
				);
				
	register_8 register3 (
					.clk(clk),
					.clr(clr),
					.en(en2reg[2]),
					.CRW(CRW),
					.D(Din),
					.Q(reg_data3)
				);
	
	register_8 register4 (
					.clk(clk),
					.clr(clr),
					.en(en2reg[3]),
					.CRW(CRW),
					.D(Din),
					.Q(reg_data4)
				);
	
    wire [7:0] mux_out;
    mux_4 mux_4 (
    .A(A_read),
    .D0(reg_data1),
    .D1(reg_data2),
    .D2(reg_data3),
    .D3(reg_data4),
    .Y(mux_out)
);

    tristate_gate tristate_gate (
        .Din(mux_out),
        .en(en_tri),
        .Dout(Dout)
    );

endmodule