module adder8421(ain, bin, sum, co);
	input wire [3:0] ain;
	input wire [3:0] bin;
	output reg [3:0] sum;
	output reg co;
	
	reg [4:0] sumtemp ;
	always @(*)
		begin
			sumtemp = ain + bin;
			if (sumtemp > 5'd9 )   // еп9╪с6
				begin
					sum = sumtemp + 5'd6;
					co = 1'b1;
				end
			else
				begin
					sum = sumtemp[3:0] ;
					co = 1'b0 ;
				end
		end
endmodule