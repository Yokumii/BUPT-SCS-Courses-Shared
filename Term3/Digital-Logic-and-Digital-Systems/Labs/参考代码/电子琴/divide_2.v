module divide_2(clk_in, clr, clk_out);
    input clk_in;
    input clr;
    output reg clk_out;

    always @(posedge clk_in, negedge clr) begin
        if (!clr) 
            clk_out <= 0;
        else 
            clk_out <= ~clk_out;
    end
endmodule