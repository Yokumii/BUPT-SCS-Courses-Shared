module m_counter(clk, clr, m, out);
    input clk;
    input clr;
    input [15:0] m;
    output reg out;

    reg [15:0] count;

    always @(posedge clk, negedge clr) begin
        if (!clr) begin
            count <= 16'd0;
            out <= 0;
        end
        else if (m != 16'd0) begin
            if (count == m - 1) begin
                count <= 16'd0;
                out <= ~out;
            end
            else begin
                count <= count + 1;
            end
        end
    end
endmodule