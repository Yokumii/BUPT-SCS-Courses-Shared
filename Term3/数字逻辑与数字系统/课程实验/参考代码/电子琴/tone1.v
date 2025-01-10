module tone1(clk, k, clkout);
    input wire clk;
    input wire [12:0] k;
    output wire clkout;
    
    reg [12:0] count;
    reg temp1, temp2;
    
    
    always @(posedge clk)
		begin
			if (count == k)
				begin
					count <= 13'd0;
				end
			else
				begin
					count <= count + 1;
				end
		end
			
	always @(posedge clk)
		begin
			if (count == k / 2)
				begin
					temp1 <= 1'b1;
				end
			else if (count == k)
				begin
					temp1 <= 1'b0;
				end
			else
				begin
					temp1 <= temp1;
				end
		end
	
	always @(negedge clk)
		begin
			if (count == k / 2)
				begin
					temp2 <= 1'b1;
				end
			else if (count == k)
				begin
					temp2 <= 1'b0;
				end
			else
				begin
					temp2 <= temp2;
				end
		end
	
	assign clkout = temp1 | temp2;

endmodule