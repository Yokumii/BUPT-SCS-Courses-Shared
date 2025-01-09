module G(IN1, IN2, IN3, IN4, IN5, IN6, IN7, OUT4);
	input IN1, IN2, IN3, IN4, IN5, IN6, IN7;
	output OUT4;
	
	wire OUT1, OUT2, OUT3;
	
	G1 G1(
		.IN1(IN1),
		.IN2(IN2),
		.IN3(IN3),
		.OUT(OUT1)
		);
	
	G2 G2(
		.IN1(IN4),
		.IN2(IN5),
		.OUT(OUT2)
		);
	
	G2 G3(
		.IN1(IN6),
		.IN2(IN7),
		.OUT(OUT3)
		);
	
	G4 G4(
		.IN1(OUT1),
		.IN2(OUT2),
		.IN3(OUT3),
		.OUT(OUT4)
		);
endmodule