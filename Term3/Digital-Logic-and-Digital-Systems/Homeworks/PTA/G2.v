module G2(IN1, IN2, OUT);
	input IN1, IN2;
	output OUT;
		
	assign OUT = ~(IN1 & IN2);
endmodule