module comp (ain, bin, aL , aE , aG, f1 ,f2 ,f3 );
	parameter n = 4;
	
	input wire [n - 1: 0] ain;
	input wire [n - 1: 0] bin;
	
	input wire aL, aE, aG;
	output reg f1, f2, f3;
	
	always @(*)
		begin
			f1 = 1'b0;
			f2 = 1'b0;
			f3 = 1'b0;
			if (ain < bin)
				begin
					f1 = 1'b1;
					f2 = 1'b0;
					f3 = 1'b0;
				end
			else if (ain > bin)
				begin
					f1 = 1'b0;
					f2 = 1'b0;
					f3 = 1'b1;
				end
			else
				begin
					case ({aL, aE, aG})
						3'b100:
							begin
								f1 = 1'b1;
								f2 = 1'b0;
								f3 = 1'b0;
							end
						3'b010:
							begin
								f1 = 1'b0;
								f2 = 1'b1;
								f3 = 1'b0;
							end
						3'b001:
							begin
								f1 = 1'b0;
								f2 = 1'b0;
								f3 = 1'b1;
							end
						default:
							begin
								f1 = 1'b0;
								f2 = 1'b0;
								f3 = 1'b0;
							end
					 endcase
                end
	end
endmodule