module lab6_counter60(clk, clr, method, Y1, Y2);
    input wire clk;
    input wire clr;
    input wire method;
    output wire [3:0] Y1;
    output wire [3:0] Y2;
    
    wire [5:0] Q;
    wire co;

    counter_60 u_counter_60 (
        .clk(clk),
        .clr(clr),
        .method(method),
        .Q(Q),
        .co(co)
    );

    display_7 u_display_7 (
        .Q(Q),
        .Y1(Y1),
        .Y2(Y2)
    );

endmodule