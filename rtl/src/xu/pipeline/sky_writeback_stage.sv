module sky_writeback_stage (
  // inputs from memory stage
  input wire [31:0] result_in,
  input wire [31:0] mem_data,
  input wire [3:0] wb_rd_addr,
  input wire wb_reg_write,
  input wire wb_from_mem,

  // register file interface
  output wire rf_write_enable,
  output wire [3:0] rf_write_addr,
  output wire [31:0] rf_write_data
);

// select data to writeback (alu or memory)
assign rf_write_data = wb_from_mem ? mem_data : result_in;
assign rf_write_addr = wb_rd_addr;
assign rf_write_enable = wb_reg_write;

endmodule
