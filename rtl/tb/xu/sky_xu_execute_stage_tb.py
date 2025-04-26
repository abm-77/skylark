import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test
async def test_execute_stage_reset(dut):
    """Test that execute stage resets properly"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    dut.stall.value = 0
    dut.pc_in.value = 0
    dut.operand_a.value = 0
    dut.operand_b.value = 0
    dut.rd_addr.value = 0
    dut.alu_op.value = 0
    dut.mem_read.value = 0
    dut.mem_write.value = 0
    dut.reg_write.value = 0
    dut.store_data.value = 0
    
    # Simulate ALU outputs
    dut.alu_result.value = 0
    dut.alu_zero_flag.value = 0
    dut.alu_overflow_flag.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check outputs are reset
    assert dut.result.value == 0, "result not reset"
    assert dut.mem_addr.value == 0, "mem_addr not reset"
    assert dut.mem_write_data.value == 0, "mem_write_data not reset"
    assert dut.wb_rd_addr.value == 0, "wb_rd_addr not reset"
    assert dut.wb_mem_read.value == 0, "wb_mem_read not reset"
    assert dut.wb_mem_write.value == 0, "wb_mem_write not reset"
    assert dut.wb_reg_write.value == 0, "wb_reg_write not reset"
    
    # Release reset
    dut.reset.value = 0

@cocotb.test
async def test_alu_operation(dut):
    """Test ALU operation in execute stage"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set inputs for an ADD operation
    dut.pc_in.value = 0x100
    dut.operand_a.value = 0x30
    dut.operand_b.value = 0x40
    dut.rd_addr.value = 5
    dut.alu_op.value = 0  # ADD operation
    dut.mem_read.value = 0
    dut.mem_write.value = 0
    dut.reg_write.value = 1
    dut.store_data.value = 0
    
    # Simulate ALU outputs (30 + 40 = 70)
    dut.alu_result.value = 0x70
    dut.alu_zero_flag.value = 0
    dut.alu_overflow_flag.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check ALU inputs are correctly connected
    assert dut.alu_operand_a.value == 0x30, f"alu_operand_a should be 0x30, got {hex(dut.alu_operand_a.value)}"
    assert dut.alu_operand_b.value == 0x40, f"alu_operand_b should be 0x40, got {hex(dut.alu_operand_b.value)}"
    assert dut.alu_operation.value == 0, f"alu_operation should be 0, got {dut.alu_operation.value}"
    
    # Check results are passed through
    assert dut.result.value == 0x70, f"result should be 0x70, got {hex(dut.result.value)}"
    assert dut.wb_rd_addr.value == 5, f"wb_rd_addr should be 5, got {dut.wb_rd_addr.value}"
    assert dut.wb_reg_write.value == 1, f"wb_reg_write should be 1, got {dut.wb_reg_write.value}"

@cocotb.test
async def test_load_store_address(dut):
    """Test load/store address calculation"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set inputs for a load operation (base address + offset)
    dut.pc_in.value = 0x100
    dut.operand_a.value = 0x1000  # Base address
    dut.operand_b.value = 0x20    # Offset
    dut.rd_addr.value = 3
    dut.alu_op.value = 0  # ADD operation for address calculation
    dut.mem_read.value = 1
    dut.mem_write.value = 0
    dut.reg_write.value = 1
    dut.store_data.value = 0
    
    # Simulate ALU outputs (base + offset = 0x1020)
    dut.alu_result.value = 0x1020
    dut.alu_zero_flag.value = 0
    dut.alu_overflow_flag.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check memory address is calculated correctly
    assert dut.mem_addr.value == 0x1020, f"mem_addr should be 0x1020, got {hex(dut.mem_addr.value)}"
    assert dut.wb_mem_read.value == 1, f"wb_mem_read should be 1, got {dut.wb_mem_read.value}"
    
    # Now test a store operation
    dut.mem_read.value = 0
    dut.mem_write.value = 1
    dut.reg_write.value = 0
    dut.store_data.value = 0xABCD  # Data to store
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check store data is passed through
    assert dut.mem_write_data.value == 0xABCD, f"mem_write_data should be 0xABCD, got {hex(dut.mem_write_data.value)}"
    assert dut.wb_mem_write.value == 1, f"wb_mem_write should be 1, got {dut.wb_mem_write.value}"

@cocotb.test
async def test_stall(dut):
    """Test that pipeline registers aren't updated when stalled"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set some initial values
    dut.pc_in.value = 0x100
    dut.operand_a.value = 0x10
    dut.operand_b.value = 0x20
    dut.rd_addr.value = 5
    dut.alu_op.value = 0
    dut.reg_write.value = 1
    dut.alu_result.value = 0x30
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Remember current values
    initial_result = dut.result.value
    
    # Now stall and change inputs
    dut.stall.value = 1
    dut.pc_in.value = 0x200
    dut.operand_a.value = 0x50
    dut.operand_b.value = 0x60
    dut.alu_result.value = 0x110
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check values didn't change despite new inputs
    assert dut.result.value == initial_result, f"result should not change during stall"
