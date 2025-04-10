module sky_register_file(
  input wire clk,
  input wire reset,

  input wire [3:0] read_addr1,
  input wire [3:0] read_addr2,
  output wire [31:0] read_data1,
  output wire [31:0] read_data2,

  input wire write_enable,
  input wire [3:0] write_addr,
  input wire [31:0] write_data
);

// each skylark XU has 16 32-bit registers
localparam NUM_REGISTERS = 16;
reg [31:0] registers [0:NUM_REGISTERS-1];

integer i;

always @(posedge clk or posedge reset) begin
  if (reset) begin
    // clear registers
    for (i = 0; i < NUM_REGISTERS; i = i + 1) begin
      registers[i] <= 32'h0;
    end
  end
  // write data to register if write enabled
  // data is written synchronously
  else if (write_enable) begin
    if (write_addr != 4'h0) registers[write_addr] <= write_data;
  end
end

assign read_data1 = (read_addr1 == 4'h0) ? 32'h0 : registers[read_addr1];
assign read_data2 = (read_addr2 == 4'h0) ? 32'h0 : registers[read_addr2];

endmodule
