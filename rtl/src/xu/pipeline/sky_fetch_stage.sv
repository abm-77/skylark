module sky_fetch_stage(
  input wire clk,
  input wire reset,
  input wire stall,
  input wire [31:0] branch_target,
  input wire branch_taken,
  output reg [31:0] pc_out,
  output reg [31:0] instruction
);

reg [31:0] pc;

reg [31:0] instr_mem[0:1023];

always @(posedge clk or posedge reset) begin
  if (reset) pc <= 32'h0;
  else if (!stall) pc <= branch_taken ? branch_target :  pc + 4;
end

always @(posedge clk) begin
  if (!stall) begin
    instruction <= instr_mem[pc[11:2]];
    pc_out <= pc;
  end
end

endmodule
