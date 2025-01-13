module counter60(clk, clr, count, co);
	input clk;
	input clr;
	
	output reg[5:0] count; // 2^6 = 64,tongbuqing0,000000->111011
	output reg co;
	
	always @(posedge clk)
		begin
			if (!clr)
				begin
					count <= 6'b0;
					co <= 1'b0;
				end
			else
				begin
					if (count == 6'd59)
						begin
							count <= 6'b0;
							co <= 1'b1;
						end
					else
						begin
							count <= count + 1;
							co <= 1'b0;
						end
				end
		end
endmodule