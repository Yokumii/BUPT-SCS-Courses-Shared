module G1(IN1, IN2, IN3, OUT);
	input IN1, IN2, IN3;
	output OUT;
	
	assign OUT = ~(IN1 & IN2 & IN3);
endmodule