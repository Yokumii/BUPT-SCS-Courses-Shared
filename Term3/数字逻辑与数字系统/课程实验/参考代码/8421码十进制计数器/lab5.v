module lab5(clk, clr, Y);
    input wire clk;
    input wire clr;
    output wire [6:0] Y;

    wire [3:0] Q;

    counter_8421 u1 (
        .clk(clk),
        .clr(clr),
        .Q(Q)
    );

    display7 u2 (
        .Q(Q),
        .Y(Y)
    );

endmodule