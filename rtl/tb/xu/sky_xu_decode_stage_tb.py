import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test
async def test_decode_stage_reset(dut):
    """Test that decode stage resets properly"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.reset.value = 1
    dut.stall.value = 0
    dut.pc_in.value = 0
    dut.instruction.value = 0
    dut.rf_read_data1.value = 0
    dut.rf_read_data2.value = 0
    dut.wb_reg_write.value = 0
    dut.wb_write_addr.value = 0
    dut.wb_write_data.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check outputs are reset
    assert dut.operand_a.value == 0, "operand_a not reset"
    assert dut.operand_b.value == 0, "operand_b not reset"
    assert dut.rd_addr.value == 0, "rd_addr not reset"
    assert dut.alu_op.value == 0, "alu_op not reset"
    assert dut.mem_read.value == 0, "mem_read not reset"
    assert dut.mem_write.value == 0, "mem_write not reset"
    assert dut.reg_write.value == 0, "reg_write not reset"
    
    dut.reset.value = 0

@cocotb.test
async def test_r_type_instruction_decode(dut):
    """Test R-type instruction decoding"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set up an R-type ADD instruction (opcode=0000, rs1=1, rs2=2, rd=3, funct=0000 for ADD)
    # Format: [31:28]=opcode, [27:24]=rs1, [23:20]=rs2, [19:16]=rd, [15:12]=funct, [11:0]=unused
    dut.instruction.value = 0x01230000
    dut.pc_in.value = 0x100
    
    # Setup register read values
    dut.rf_read_data1.value = 0x10
    dut.rf_read_data2.value = 0x20
    
    # No forwarding
    dut.wb_reg_write.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check register addresses are correctly extracted
    assert dut.rf_read_addr1.value == 1, f"rs1 should be 1, got {dut.rf_read_addr1.value}"
    assert dut.rf_read_addr2.value == 2, f"rs2 should be 2, got {dut.rf_read_addr2.value}"
    
    # Check operands and control signals
    assert dut.operand_a.value == 0x10, f"operand_a should be 0x10, got {hex(dut.operand_a.value)}"
    assert dut.operand_b.value == 0x20, f"operand_b should be 0x20, got {hex(dut.operand_b.value)}"
    assert dut.rd_addr.value == 3, f"rd should be 3, got {dut.rd_addr.value}"
    assert dut.alu_op.value == 0, f"alu_op should be ADD (0), got {dut.alu_op.value}"
    assert dut.reg_write.value == 1, f"reg_write should be 1 for R-type"
    assert dut.mem_read.value == 0, f"mem_read should be 0 for R-type"
    assert dut.mem_write.value == 0, f"mem_write should be 0 for R-type"

@cocotb.test
async def test_i_type_instruction_decode(dut):
    """Test I-type instruction decoding with immediate operand"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    await RisingEdge(dut.clk)

    # Set up an I-type ADDI instruction 
    # opcode=0001 (I-type), rs1=1, rd=3, funct=0 (ADD), imm=0x234
    dut.instruction.value = 0x11330123
    dut.pc_in.value = 0x100
    
    # Setup register read value
    dut.rf_read_data1.value = 0x10
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Check register addresses
    assert dut.rf_read_addr1.value == 1, f"rs1 should be 1, got {dut.rf_read_addr1.value}"
    
    # Check operands and control signals
    assert dut.operand_a.value == 0x10, f"operand_a should be 0x10, got {hex(dut.operand_a.value)}"
  
    # Check immediate with sign extension (0x1234 should be sign extended to 0x00001234)
    assert dut.operand_b.value == 0x123, f"operand_b should be 0x1234, got {hex(dut.operand_b.value)}"
    assert dut.rd_addr.value == 3, f"rd should be 3, got {dut.rd_addr.value}"
    assert dut.alu_op.value == 0, f"alu_op should be ADD (0), got {dut.alu_op.value}"
    assert dut.reg_write.value == 1, f"reg_write should be 1 for I-type"

@cocotb.test
async def test_forwarding(dut):
    """Test register forwarding from writeback stage"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Setup an R-type instruction using rs1=1 and rs2=2
    dut.instruction.value = 0x01230000  # rs1=1, rs2=2
    dut.pc_in.value = 0x100
    
    # Setup normal register read values
    dut.rf_read_data1.value = 0x10
    dut.rf_read_data2.value = 0x20
    
    # Setup forwarding from writeback stage to rs1
    dut.wb_reg_write.value = 1
    dut.wb_write_addr.value = 1  # Forwarding to rs1
    dut.wb_write_data.value = 0xABCD
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check forwarded data is used for operand_a
    assert dut.operand_a.value == 0xABCD, f"operand_a should be forwarded value 0xABCD, got {hex(dut.operand_a.value)}"
    assert dut.operand_b.value == 0x20, f"operand_b should be original reg value 0x20, got {hex(dut.operand_b.value)}"
    
    # Change forwarding to rs2
    dut.wb_write_addr.value = 2  # Forwarding to rs2
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check forwarded data is used for operand_b
    assert dut.operand_a.value == 0x10, f"operand_a should be original reg value 0x10, got {hex(dut.operand_a.value)}"
    assert dut.operand_b.value == 0xABCD, f"operand_b should be forwarded value 0xABCD, got {hex(dut.operand_b.value)}"
