module sky_data_memory(
  input wire clk,
  input wire reset,
  input wire [31:0] address,
  input wire write_enable,
  input wire read_enable,
  input wire [31:0] write_data,
  output reg [31:0] read_data
);

  reg [31:0] memory [0:1023]; // 1K memory
  
  integer i;
  
  always @(posedge clk) begin
    if (reset) begin
      for (i = 0; i < 1024; i = i + 1) begin
        memory[i] <= 32'h0;
      end
    end else begin
      if (write_enable) begin
        memory[address[11:2]] <= write_data;
      end
      
      if (read_enable) begin
        read_data <= memory[address[11:2]];
      end
    end
  end

endmodule

module sky_xu(
  input wire clk,
  input wire reset,
);

// pipeline stage connections
wire [31:0] if_pc, if_instruction;
wire [31:0] id_pc, id_operand_a, id_operand_b, id_store_data;
wire [3:0] id_rd_addr, id_alu_op;
wire id_mem_read, id_mem_write, id_reg_write;

wire [31:0] ex_result, ex_mem_addr, ex_mem_write_data;
wire [3:0] ex_wb_rd_addr;
wire ex_wb_mem_read, ex_wb_mem_write, ex_wb_reg_write;
wire ex_branch_taken;
wire [31:0] ex_branch_target;

wire [31:0] mem_result, mem_data;
wire [3:0] mem_wb_rd_addr;
wire mem_wb_reg_write, mem_wb_from_mem;

// register file connections
wire [3:0] rf_read_addr1, rf_read_addr2;
wire [31:0] rf_read_data1, rf_read_data2;
wire rf_write_enable;
wire [3:0] rf_write_addr;
wire [31:0] rf_write_data;

// ALU connections
wire [31:0] alu_operand_a, alu_operand_b, alu_result;
wire [3:0] alu_operation;
wire alu_zero_flag, alu_overflow_flag;

// memory connections
wire [31:0] mem_address, mem_write_data_out, mem_read_data;
wire mem_read_en, mem_write_en;

// hazard and forwarding control (simplified)
wire pipeline_stall = 1'b0; // would be connected to hazard detection

sky_fetch_stage fetch(
  .clk(clk),
  .reset(reset),
  .stall(pipeline_stall),
  .branch_target(ex_branch_target),
  .branch_taken(ex_branch_taken),
  .pc_out(if_pc),
  .instruction(if_instruction)
);

sky_decode_stage decode(
  .clk(clk),
  .reset(reset),
  .stall(pipeline_stall),
  .pc_in(if_pc),
  .instruction(if_instruction),
  .rf_read_addr1(rf_read_addr1),
  .rf_read_addr2(rf_read_addr2),
  .rf_read_data1(rf_read_data1),
  .rf_read_data2(rf_read_data2),
  .wb_reg_write(rf_write_enable),
  .wb_write_addr(rf_write_addr),
  .wb_write_data(rf_write_data),
  .pc_out(id_pc),
  .operand_a(id_operand_a),
  .operand_b(id_operand_b),
  .rd_addr(id_rd_addr),
  .alu_op(id_alu_op),
  .mem_read(id_mem_read),
  .mem_write(id_mem_write),
  .reg_write(id_reg_write),
  .store_data(id_store_data)
);

sky_execute_stage execute(
  .clk(clk),
  .reset(reset),
  .stall(pipeline_stall),
  .pc_in(id_pc),
  .operand_a(id_operand_a),
  .operand_b(id_operand_b),
  .rd_addr(id_rd_addr),
  .alu_op(id_alu_op),
  .mem_read(id_mem_read),
  .mem_write(id_mem_write),
  .reg_write(id_reg_write),
  .store_data(id_store_data),
  .alu_operand_a(alu_operand_a),
  .alu_operand_b(alu_operand_b),
  .alu_operation(alu_operation),
  .alu_result(alu_result),
  .alu_zero_flag(alu_zero_flag),
  .alu_overflow_flag(alu_overflow_flag),
  .branch_taken(ex_branch_taken),
  .branch_target(ex_branch_target),
  .result(ex_result),
  .mem_addr(ex_mem_addr),
  .mem_write_data(ex_mem_write_data),
  .wb_rd_addr(ex_wb_rd_addr),
  .wb_mem_read(ex_wb_mem_read),
  .wb_mem_write(ex_wb_mem_write),
  .wb_reg_write(ex_wb_reg_write)
);

sky_memory_stage memory(
  .clk(clk),
  .reset(reset),
  .stall(pipeline_stall),
  .result_in(ex_result),
  .mem_addr(ex_mem_addr),
  .mem_write_data(ex_mem_write_data),
  .wb_rd_addr_in(ex_wb_rd_addr),
  .wb_mem_read(ex_wb_mem_read),
  .wb_mem_write(ex_wb_mem_write),
  .wb_reg_write_in(ex_wb_reg_write),
  .mem_address(mem_address),
  .mem_read_en(mem_read_en),
  .mem_write_en(mem_write_en),
  .mem_write_data_out(mem_write_data_out),
  .mem_read_data(mem_read_data),
  .result_out(mem_result),
  .mem_data(mem_data),
  .wb_rd_addr_out(mem_wb_rd_addr),
  .wb_reg_write_out(mem_wb_reg_write),
  .wb_from_mem(mem_wb_from_mem)
);

sky_writeback_stage writeback(
  .result_in(mem_result),
  .mem_data(mem_data),
  .wb_rd_addr(mem_wb_rd_addr),
  .wb_reg_write(mem_wb_reg_write),
  .wb_from_mem(mem_wb_from_mem),
  .rf_write_enable(rf_write_enable),
  .rf_write_addr(rf_write_addr),
  .rf_write_data(rf_write_data)
);

sky_register_file regfile(
  .clk(clk),
  .reset(reset),
  .read_addr1(rf_read_addr1),
  .read_addr2(rf_read_addr2),
  .read_data1(rf_read_data1),
  .read_data2(rf_read_data2),
  .write_enable(rf_write_enable),
  .write_addr(rf_write_addr),
  .write_data(rf_write_data)
);

sky_alu alu(
  .clk(clk),
  .reset(reset),
  .operand_a(alu_operand_a),
  .operand_b(alu_operand_b),
  .operation(alu_operation),
  .result(alu_result),
  .zero_flag(alu_zero_flag),
  .overflow_flag(alu_overflow_flag)
);

sky_data_memory data_mem(
  .clk(clk),
  .reset(reset),
  .address(mem_address),
  .write_enable(mem_write_en),
  .read_enable(mem_read_en),
  .write_data(mem_write_data_out),
  .read_data(mem_read_data)
);
endmodule

