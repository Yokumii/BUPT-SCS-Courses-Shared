module display7(Q, Y);
	input wire [3:0] Q;
	
	output reg [6:0] Y;
	
	always @(*)
		begin
			case(Q)
				4'b0000: Y = 7'b0111111;
				4'b0001: Y = 7'b0000110;
				4'b0010: Y = 7'b1011011;
				4'b0011: Y = 7'b1001111;
				4'b0100: Y = 7'b1100110;
				4'b0101: Y = 7'b1101101;
				4'b0110: Y = 7'b1111101;
				4'b0111: Y = 7'b0000111;
				4'b1000: Y = 7'b1111111;
				4'b1001: Y = 7'b1101111;
				default: Y = 7'b0000000;
			endcase
		end
endmodule