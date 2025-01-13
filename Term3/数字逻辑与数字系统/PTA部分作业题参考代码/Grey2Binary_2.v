module Grey2Binary_2;
    reg [3:0] gray;
    wire [3:0] binary;

    // 实例化模块
    gray_to_binary uut (
        .gray(gray),
        .binary(binary)
    );

    initial begin
        // 打印标题
        $display("Gray Code | Binary Code");
        $monitor("%b      | %b", gray, binary);
        
        // 测试用例
        gray = 4'b0000; #10; // Gray: 0000 -> Binary: 0000
        gray = 4'b0001; #10; // Gray: 0001 -> Binary: 0001
        gray = 4'b0011; #10; // Gray: 0011 -> Binary: 0010
        gray = 4'b0010; #10; // Gray: 0010 -> Binary: 0011
        gray = 4'b0110; #10; // Gray: 0110 -> Binary: 0100
        gray = 4'b0111; #10; // Gray: 0111 -> Binary: 0101
        gray = 4'b0101; #10; // Gray: 0101 -> Binary: 0110
        gray = 4'b0100; #10; // Gray: 0100 -> Binary: 0111
        gray = 4'b1100; #10; // Gray: 1100 -> Binary: 1000
        gray = 4'b1101; #10; // Gray: 1101 -> Binary: 1001
        gray = 4'b1111; #10; // Gray: 1111 -> Binary: 1010
        gray = 4'b1110; #10; // Gray: 1110 -> Binary: 1011
        $finish;
    end
endmodule