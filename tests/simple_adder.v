module simple_adder (
    input wire clk_i,
    input wire rst_ni,
    
    // Data Inputs
    input wire [31:0] a_i,
    input wire [31:0] b_i,
    input wire        valid_i,
    
    // Data Output
    output reg [32:0] sum_o,
    output reg        valid_o
);

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            sum_o   <= 33'd0;
            valid_o <= 1'b0;
        end else if (valid_i) begin
            sum_o   <= a_i + b_i;
            valid_o <= 1'b1;
        end else begin
            valid_o <= 1'b0;
        end
    end

endmodule
