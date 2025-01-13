module Suber(A, B, Cin, Cout, D);
	parameter n = 4;
	
	input wire [n - 1:0] A;
	input wire [n - 1:0] B;
	input wire Cin;

	output reg [n - 1:0] D;
	output reg Cout;
	
	reg [n : 0] C;
	
	integer k;
	
	always @(*)
		begin
			C[0] = Cin;
			for (k = 0; k < n; k = k + 1)
				begin
					D[k] = A[k] ^ B[k] ^ C[k];
					C[k + 1] = (~A[k] & (B[k] | C[k])) | (B[k] & C[k]);
				end
			Cout = C[n];
		end
endmodule