module counter_60(clk, clr, method, Q, co);
    input wire clk;
    input wire clr;
    input wire method;
    
    output reg [5:0] Q;
    output reg co;

    always @(posedge clk, negedge clr)
		begin
			if (!clr)
				begin
					Q <= 6'd0;
					co <= 1'b0;
				end
			else
				begin
					if (method)
						begin
							if (Q == 6'd59)
								begin
									Q <= 6'd0;
									co <= 1'b1;
								end
							else
								begin
									Q <= Q + 1;
									co <= 1'b0;
								end
						end
					else
						begin
							if (Q == 6'd0)
								begin
									Q <= 6'd59;
									co <= 1'b1;
								end
							else
								begin
									Q <= Q - 1;
									co <= 1'b0;
								end
						end
				end
		end
endmodule