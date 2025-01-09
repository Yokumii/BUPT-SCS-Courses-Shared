module display_7(Q, Y1, Y2);
	input [5:0] Q;
	
	output [3:0] Y1;
	
	output [3:0] Y2;
	
	assign Y1 = Q / 10;
	assign Y2 = Q % 10;
endmodule