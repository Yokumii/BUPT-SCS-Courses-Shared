module shift_reg4(clk, D, Q);
	input clk;
	input D;
	
	output Q;
	
	wire [2:0] qtemp;
	
    base_reg u0 (
        .clk(clk),
        .d(D),
        .q(qtemp[0])
    );

    base_reg u1 (
        .clk(clk),
        .d(qtemp[0]),
        .q(qtemp[1])
    );

    base_reg u2 (
        .clk(clk),
        .d(qtemp[1]),
        .q(qtemp[2])
    );

    base_reg u3 (
        .clk(clk),
        .d(qtemp[2]),
        .q(Q)
    );
    
endmodule