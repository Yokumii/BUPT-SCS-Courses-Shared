module electronic_piano(clk, keys, speaker);
    input wire clk;
    input wire [7:0] keys;
    output wire speaker;
    
    reg [12:0] div_factor;
    reg is_odd;
    
    wire even_clk_out;
    wire odd_clk_out;

    reg [12:0] tone_table [7:0];
    initial begin
        tone_table[0] = 3817;
        tone_table[1] = 3400;
        tone_table[2] = 3030;
        tone_table[3] = 2865;
        tone_table[4] = 2551;
        tone_table[5] = 2272;
        tone_table[6] = 2024;
        tone_table[7] = 1911;
    end

    always @(*) begin
        case (keys)
            8'b00000001: div_factor = tone_table[0];
            8'b00000010: div_factor = tone_table[1];
            8'b00000100: div_factor = tone_table[2];
            8'b00001000: div_factor = tone_table[3];
            8'b00010000: div_factor = tone_table[4];
            8'b00100000: div_factor = tone_table[5];
            8'b01000000: div_factor = tone_table[6];
            8'b10000000: div_factor = tone_table[7];
            default: div_factor = 0;
        endcase
        is_odd = div_factor[0];
    end

    tone2 even_inst (
        .clk(clk),
        .k(div_factor),
        .clkout(even_clk_out)
    );

    tone1 odd_inst (
        .clk(clk),
        .k(div_factor),
        .clkout(odd_clk_out)
    );

    assign speaker = (keys != 8'b00000000) ? (is_odd ? odd_clk_out : even_clk_out) : 1'b0;
endmodule