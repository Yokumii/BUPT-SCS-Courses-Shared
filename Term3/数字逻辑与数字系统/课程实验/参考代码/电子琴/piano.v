module piano(clk, clr, key, speaker);
    input clk;
    input clr;
    input [7:0] key;
    output speaker;

    wire [15:0] m;
    wire m_clk;
    wire speaker_clk;

    key_to_freq key_to_freq_inst (
        .key(key),
        .m(m)
    );

    m_counter m_counter_inst (
        .clk(clk),
        .clr(clr),
        .m(m),
        .out(m_clk)
    );

    divide_2 divide_2_inst (
        .clk_in(m_clk),
        .clr(clr),
        .clk_out(speaker_clk)
    );
	
	assign speaker = speaker_clk;
endmodule
