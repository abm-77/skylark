module sky_memory_stage(
  input wire clk,
  input wire reset,
  input wire stall,

  // inputs from execute stage
  input wire [31:0] result_in,
  input wire [31:0] mem_addr,
  input wire [31:0] mem_write_data,
  input wire [3:0] wb_rd_addr_in,
  input wire wb_mem_read,
  input wire wb_mem_write,
  input wire wb_reg_write_in,

  // memory interface 
  output wire[31:0] mem_address,
  output wire mem_read_en,
  output wire mem_write_en,
  output wire[31:0] mem_write_data_out,
  output wire [31:0] mem_read_data,

  // outputs to writeback stage
  output reg [31:0] result_out,
  output reg [31:0] mem_data,
  output reg [3:0] wb_rd_addr_out,
  output reg wb_reg_write_out,
  output reg wb_from_mem
);

// memory control signals
assign mem_address = mem_addr;
assign mem_read_en = wb_mem_read;
assign mem_write_en = wb_mem_write;
assign mem_write_data_out = mem_write_data;

always @(posedge clk or posedge reset) begin
  if (reset) begin
    result_out <= 32'h0;
    mem_data <= 32'h0;
    wb_rd_addr_out <= 4'h0;
    wb_reg_write_out <= 1'b0;
    wb_from_mem <= 1'b0;
  end else if (!stall) begin
    result_out <= result_in;
    mem_data <= mem_read_data;
    wb_rd_addr_out <= wb_rd_addr_in;
    wb_reg_write_out <= wb_reg_write_in;
    wb_from_mem <= wb_mem_read;
  end
end

endmodule
