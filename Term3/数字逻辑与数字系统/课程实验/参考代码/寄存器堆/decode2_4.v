module decode2_4(A, en_decode, Y);
	input wire [1:0] A;
	input wire en_decode;
	
	output reg [3:0] Y;
	
	always @(*)
		begin
			if (en_decode)
				begin
					Y = 4'b1111;
				end
			else
				begin
					case(A)
						2'b00: Y = 4'b1110;
						2'b01: Y = 4'b1101;
						2'b10: Y = 4'b1011;
						2'b11: Y = 4'b0111;
						default: Y = 4'b1111;
					endcase
				end
		end
endmodule