module register_8(clk, clr, D, Q, en, CRW);
	input clk;
	input wire clr;
	input wire en;
	input wire CRW;
	input wire[7: 0] D;
	
	output reg[7: 0] Q;
	
	always @(posedge clk, negedge clr)
		begin
			if (!clr)
				Q <= 8'b0;
			else if (!en && CRW)
				Q <= D;
			else
				Q <= Q;
		end
endmodule