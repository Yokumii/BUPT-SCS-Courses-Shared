module counter_8421(clk, clr, Q);
    input wire clk;
    input wire clr;
    output reg [3:0] Q;

    always @(posedge clk ,negedge clr)
		begin
        if (!clr)
			begin
				Q <= 4'b0;
			end
		else
			begin
				if (Q == 4'b1001)
					begin
						Q <= 4'b0;
					end
				else
					begin
						Q <= Q + 1;
					end
			end
		end
endmodule