module sky_execute_stage(
  input wire clk,
  input wire reset,
  input wire stall,

  // inputs from Decode stage
  input wire [31:0] pc_in,
  input wire [31:0] operand_a,
  input wire [31:0] operand_b,
  input wire [3:0] rd_addr,
  input wire [3:0] alu_op,
  input wire mem_read,
  input wire mem_write,
  input wire reg_write,
  input wire [31:0] store_data,
  
  // ALU interface
  output wire [31:0] alu_operand_a,
  output wire [31:0] alu_operand_b,
  output wire [3:0] alu_operation,
  input wire [31:0] alu_result,
  input wire alu_zero_flag,
  input wire alu_overflow_flag,
  
  // branch control
  output reg branch_taken,
  output reg [31:0] branch_target,
  
  // outputs to Memory stage
  output reg [31:0] result,
  output reg [31:0] mem_addr,
  output reg [31:0] mem_write_data,
  output reg [3:0] wb_rd_addr,
  output reg wb_mem_read,
  output reg wb_mem_write,
  output reg wb_reg_write
);

// connect operands to alu
assign alu_operand_a = operand_a;
assign alu_operand_b = operand_b;
assign alu_operation = alu_op;

// TODO: branch logic
always @(*) begin
  branch_taken = 1'b0;
  branch_target = 32'h0;
end

always @(posedge clk or posedge reset) begin
  if (reset) begin
    result <= 32'h0;
    mem_addr <= 32'h0;
    mem_write_data <= 32'h0;
    wb_rd_addr <= 4'h0;
    wb_mem_read <= 1'b0;
    wb_mem_write <= 1'b0;
    wb_reg_write <= 1'b0;
  end else if (!stall) begin
    result <= alu_result;
    mem_addr <= alu_result; // Address for load/store
    mem_write_data <= store_data;
    wb_rd_addr <= rd_addr;
    wb_mem_read <= mem_read;
    wb_mem_write <= mem_write;
    wb_reg_write <= reg_write;
  end
end

endmodule
