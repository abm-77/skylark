module sky_decode_stage(
  input wire clk,
  input wire reset,
  input wire stall,

  // inputs from fetch stage
  input wire [31:0] pc_in,
  input wire [31:0] instruction,

  // register file interface
  output wire [3:0] rf_read_addr1,
  output wire [3:0] rf_read_addr2,
  input wire [31:0] rf_read_data1,
  input wire [31:0] rf_read_data2,
  
  // write-back stage connections (for register forwarding)
  input wire wb_reg_write,
  input wire [3:0] wb_write_addr,
  input wire [31:0] wb_write_data,
  
  // outputs to Execute stage
  output reg [31:0] pc_out,
  output reg [31:0] operand_a,
  output reg [31:0] operand_b,
  output reg [3:0] rd_addr,
  output reg [3:0] alu_op,
  output reg mem_read,
  output reg mem_write,
  output reg reg_write,
  output reg [31:0] store_data
);

// instr fields
wire [3:0] opcode = instruction[31:28];
wire [3:0] rs1 = instruction[27:24];
wire [3:0] rs2 = instruction[23:20];
wire [3:0] rd = instruction[19:16];
wire [3:0] funct = instruction[15:12];
wire [11:0] imm = instruction[11:0];

// control signals
reg [3:0] alu_op_d;
reg mem_read_d;
reg mem_write_d;
reg reg_write_d;
reg use_imm;

// connect read addresses to reg file
assign rf_read_addr1 = rs1;
assign rf_read_addr2 = rs2;

// decode instr
always @(*) begin
  alu_op_d = 4'b0000;
  mem_read_d = 1'b0;
  mem_write_d = 1'b0;
  reg_write_d = 1'b0;
  use_imm = 1'b0;

  case (opcode)
    4'b0000: begin // r-type ops
      alu_op_d = funct;
      reg_write_d = 1'b1;
    end
    4'b0001: begin // i-type ops
      alu_op_d = funct;
      reg_write_d = 1'b1;
      use_imm = 1'b1;
    end
    4'b0010: begin // load
      alu_op_d = 4'b0000; // add for address calculation
      mem_read_d = 1'b1;
      reg_write_d = 1'b1;
      use_imm = 1'b1;
    end
    4'b0011: begin // store
      alu_op_d = 4'b0000; // add for address calculation
      mem_write_d = 1'b1;
      use_imm = 1'b1;
    end
  endcase
end

always @(posedge clk or posedge reset) begin
  if (reset) begin
    pc_out <= 32'h0;
    operand_a <= 32'h0;
    operand_b <= 32'h0;
    rd_addr <= 4'h0;
    alu_op <= 4'h0;
    mem_read <= 1'b0;
    mem_write <= 1'b0;
    reg_write <= 1'b0;
    store_data <= 32'h0;
  end else if (!stall) begin
    pc_out <= pc_in;
    alu_op <= alu_op_d;
    mem_read <= mem_read_d;
    mem_write <= mem_write_d;
    reg_write <= reg_write_d;
    rd_addr <= rd;
    
    // handle forwarding from writeback stage
    if (wb_reg_write && wb_write_addr == rs1 && rs1 != 4'h0) begin
      operand_a <= wb_write_data;
    end else begin
      operand_a <= rf_read_data1;
    end
    
    // second operand can be either register or immediate
    if (use_imm) begin
      // sign-extend immediate
      operand_b <= {{20{imm[11]}}, imm};
    end else if (wb_reg_write && wb_write_addr == rs2 && rs2 != 4'h0) begin
      operand_b <= wb_write_data;
    end else begin
      operand_b <= rf_read_data2;
    end
    
    if (wb_reg_write && wb_write_addr == rs2 && rs2 != 4'h0) begin
      store_data <= wb_write_data;
    end else begin
      store_data <= rf_read_data2;
    end
  end
end

endmodule
