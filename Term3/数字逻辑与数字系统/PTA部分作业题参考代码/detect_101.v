module detect_101(clk, rst, x, y);
	input clk, rst, x;
	output reg y;
	
	//s0 = ...00;
	//s1 = ...10;
	//s2 = ...11/01;
	//s3 = inefficient;
	parameter s0 = 2'b00, s1 = 2'b01, s2 = 2'b10, s3 = 2'b11;
	
	reg [1:0] current_state, next_state;
	
	always @(posedge clk, negedge rst)
		begin
			if (!rst)
				current_state <= s0;
			else
				current_state <= next_state;
		end
	
	always @(current_state, x)
		begin
			case(current_state)
				s0:
					begin
						if (x == 1'b0)
							begin
								next_state = s0;
								y = 1'b0;
							end
						else
							begin
								next_state = s2;
								y = 1'b0;
							end
					end
				s1:
					begin
						if (x == 1'b0)
							begin
								next_state = s0;
								y = 1'b0;
							end
						else
							begin
								next_state = s2;
								y = 1'b1;
							end
					end
				s2:
					begin
						if (x == 1'b0)
							begin
								next_state = s1;
								y = 1'b0;
							end
						else
							begin
								next_state = s2;
								y = 1'b0;
							end
					end
				s3:
					begin
						if (x == 1'b0)
							begin
								next_state = s0;
								y = 1'b0;
							end
						else
							begin
								next_state = s2;
								y = 1'b0;
							end
					end
				default:
					begin
    					next_state = s0;
    					y = 1'b0;
					end
			endcase			
		end
endmodule