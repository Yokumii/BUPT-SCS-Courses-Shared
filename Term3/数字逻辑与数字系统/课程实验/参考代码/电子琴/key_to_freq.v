module key_to_freq(key, m);
    input [7:0] key;
    output reg [15:0] m;

    always @(*) begin
        case (key)
            8'b00000001: m = 16'd1908;
            8'b00000010: m = 16'd1701;
            8'b00000100: m = 16'd1515;
            8'b00001000: m = 16'd1433;
            8'b00010000: m = 16'd1276;
            8'b00100000: m = 16'd1136;
            8'b01000000: m = 16'd1012;
            8'b10000000: m = 16'd956;
            default: m = 16'd0;
        endcase
    end
endmodule