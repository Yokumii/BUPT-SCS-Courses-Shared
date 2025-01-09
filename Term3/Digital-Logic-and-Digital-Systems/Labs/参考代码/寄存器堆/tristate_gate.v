module tristate_gate(Din, en, Dout);
    input wire [7:0] Din;
    input wire en;
    
    output wire [7:0] Dout;
	
	assign Dout = !en ? Din : 8'bz;
endmodule