module Gray_counter(clk, y, rst, cout);
	input clk;
	input rst;
	input y;
	output [2:0] cout;
	
	parameter s0 = 3'b000, s1 = 3'b001, s2 = 3'b011, s3 = 3'b010, s4 = 3'b110, s5 = 3'b111, s6 = 3'b101, s7 = 3'b100;
	
	reg [2:0] current_state, next_state;
	
	always @(posedge clk, negedge rst)
		begin
			if (!rst)
				begin
					current_state <= s0;
				end
			else
				begin
					current_state <= next_state;
				end
		end
	
	always @(current_state, y)
		begin
			case(current_state)
				s0:
					begin
						if (y == 1'b0)
							next_state = s7;
						else
							next_state = s1;
					end
				s1:
					begin
						if (y == 1'b0)
							next_state = s0;
						else
							next_state = s2;
					end
				s2:
					begin
						if (y == 1'b0)
							next_state = s1;
						else
							next_state = s3;
					end
				s3:
					begin
						if (y == 1'b0)
							next_state = s2;
						else
							next_state = s4;
					end
				s4:
					begin
						if (y == 1'b0)
							next_state = s3;
						else
							next_state = s5;
					end
				s5:
					begin
						if (y == 1'b0)
							next_state = s4;
						else
							next_state = s6;
					end
				s6:
					begin
						if (y == 1'b0)
							next_state = s5;
						else
							next_state = s7;
					end
				s7:
					begin
						if (y == 1'b0)
							next_state = s6;
						else
							next_state = s0;
					end
				default:
					next_state = s0;
			endcase
		end
	assign cout = current_state;
endmodule