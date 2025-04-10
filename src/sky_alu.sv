module sky_alu (
  input wire          clk,
  input wire          reset,
  input wire [31:0]   operand_a,
  input wire [31:0]   operand_b,
  input wire [3:0]    operation,
  output reg [31:0]   result,
  output wire         zero_flag,
  output wire         overflow_flag
);

// opcodes
localparam  
  ADD   = 4'b0000,
  SUB   = 4'b0001,
  AND   = 4'b0010,
  OR    = 4'b0011,
  XOR   = 4'b0100,
  SLL   = 4'b0101,
  SRL   = 4'b0110,
  SRA   = 4'b0111,
  SLT   = 4'b1000,
  SLTU  = 4'b1001,
  MUL   = 4'b1010;

// internal signals for overflow detection
wire signed_overflow;
wire [32:0] add_result_ext;
wire [32:0] sub_result_ext;

always @(posedge clk) begin
  if (reset) begin
    result <= 32'h0;
  end else begin 
    case (operation)
      ADD:  result <= operand_a + operand_b;
      SUB:  result <= operand_a - operand_b;
      AND:  result <= operand_a & operand_b;
      OR:   result <= operand_a | operand_b;
      XOR:  result <= operand_a ^ operand_b;
      SLL:  result <= operand_a << operand_b[4:0]; // use bottom 5 bits for shift (shifts up to 32-bits)
      SRL:  result <= operand_a >> operand_b[4:0];
      SRA:  result <= $signed(operand_a) >>> operand_b[4:0];
      SLT:  result <= $signed(operand_a) < $signed(operand_b) ? 32'h1 : 32'h0;
      SLTU: result <= operand_a < operand_b ? 32'h1 : 32'h0;
      MUL:  result <= operand_a * operand_b; // sets lower 32-bits by default
      default: result <= 32'h0;
    endcase
  end
end


assign add_result_ext = {operand_a[31], operand_a} + {operand_b[31], operand_b};
assign sub_result_ext = {operand_a[31], operand_a} - {operand_b[31], operand_b};
assign signed_overflow = (operation == ADD) ? (add_result_ext[32] != add_result_ext[31]) : (operation == SUB) ?  sub_result_ext[32] != sub_result_ext[31] : 1'b0;
assign overflow_flag = signed_overflow;
assign zero_flag = result == 0;


endmodule
