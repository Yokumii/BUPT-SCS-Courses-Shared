module reg8(clk, clr, d, q);
	input clk;
	input clr;
	input wire[7: 0] d;
	
	output reg[7: 0] q;
	
	always @(posedge clk, negedge clr)
		begin
			if (!clr)
				begin
					q <= 8'b0;
				end
			else
				begin
					q <= d;
				end
		end
endmodule