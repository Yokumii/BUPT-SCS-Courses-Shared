module tone2(clk, k, clkout);
    input wire clk;
    input wire [12:0] k;
    output wire clkout;
    
    reg [12:0] count;
    reg temp;
    
    
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
			if (count == k)
				begin
					temp <= ~temp;
				end
			else
				begin
					temp <= temp;
				end
		end
	
	assign clkout = temp;

endmodule