module demus_4 (A, D, E, F);
	input wire [1:0] A;
    input wire D;
    input wire E;
    output reg [3:0] F;
    
    always @(*)
		begin
			if (E) 
				begin
					case (A)
						2'b00: F = {3'b111, D};
						2'b01: F = {2'b11, D, 1'b1};
						2'b10: F = {1'b1, D, 2'b11};
						2'b11: F = {D, 3'b111};
						default: F = 4'b1111;
					endcase
				end
			else
				begin
					F = 4'b1111;
				end
		end
endmodule