module latch8(OE, LE, D, Q);
	input wire OE;
	input wire LE;
	input wire [7:0] D;
	
	output reg [7:0] Q;
	
	reg [7:0] temp;
	
	always @(LE, D)
		begin
			if (LE)
				begin
					temp <= D;
				end
		end
	
	always @(*)
		begin
			if (OE)
				begin
					Q = 8'bz;
				end
			else
				begin
					Q = temp;
				end
		end
endmodule