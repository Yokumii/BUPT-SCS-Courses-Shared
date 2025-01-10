module mux_4 (A, D0, D1, D2, D3, Y);
    input wire [1:0] A;
    input wire [7:0] D0, D1, D2, D3;
    
    output reg [7:0] Y;
    always @(*) begin
        case (A)
            2'b00: Y = D0;
            2'b01: Y = D1;
            2'b10: Y = D2;
            2'b11: Y = D3;
            default: Y = 8'b0;
        endcase
    end
endmodule