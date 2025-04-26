import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test
async def test_memory_stage_reset(dut):
    """Test that memory stage resets properly"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    dut.stall.value = 0
    dut.result_in.value = 0
    dut.mem_addr.value = 0
    dut.mem_write_data.value = 0
    dut.wb_rd_addr_in.value = 0
    dut.wb_mem_read.value = 0
    dut.wb_mem_write.value = 0
    dut.wb_reg_write_in.value = 0
    dut.mem_read_data.value = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check outputs are reset
    assert dut.result_out.value == 0, "result_out not reset"
    assert dut.mem_data.value == 0, "mem_data not reset"
    assert dut.wb_rd_addr_out.value == 0, "wb_rd_addr_out not reset"
    assert dut.wb_reg_write_out.value == 0, "wb_reg_write_out not reset"
    assert dut.wb_from_mem.value == 0, "wb_from_mem not reset"
    
    # Release reset
    dut.reset.value = 0

@cocotb.test
async def test_memory_read(dut):
    """Test memory read operation"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set up a memory read operation
    dut.result_in.value = 0x1000  # Address calculated in execute stage
    dut.mem_addr.value = 0x1000
    dut.wb_rd_addr_in.value = 5   # Destination register
    dut.wb_mem_read.value = 1     # Memory read operation
    dut.wb_mem_write.value = 0
    dut.wb_reg_write_in.value = 1 # Will write result to register
    
    # Simulate data coming back from memory
    dut.mem_read_data.value = 0xABCDEF01
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check memory control signals
    assert dut.mem_address.value == 0x1000, f"mem_address should be 0x1000, got {hex(dut.mem_address.value)}"
    assert dut.mem_read_en.value == 1, f"mem_read_en should be 1, got {dut.mem_read_en.value}"
    assert dut.mem_write_en.value == 0, f"mem_write_en should be 0, got {dut.mem_write_en.value}"
    
    # Check output signals
    assert dut.result_out.value == 0x1000, f"result_out should pass through input, got {hex(dut.result_out.value)}"
    assert dut.mem_data.value == 0xABCDEF01, f"mem_data should match read_data, got {hex(dut.mem_data.value)}"
    assert dut.wb_rd_addr_out.value == 5, f"wb_rd_addr_out should be 5, got {dut.wb_rd_addr_out.value}"
    assert dut.wb_reg_write_out.value == 1, f"wb_reg_write_out should be 1, got {dut.wb_reg_write_out.value}"
    assert dut.wb_from_mem.value == 1, f"wb_from_mem should be 1 for load, got {dut.wb_from_mem.value}"

@cocotb.test
async def test_memory_write(dut):
    """Test memory write operation"""
    
    # Start clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set up a memory write operation
    dut.result_in.value = 0x2000   # Address calculated in execute stage
    dut.mem_addr.value = 0x2000
    dut.mem_write_data.value = 0x12345678  # Data to write
    dut.wb_rd_addr_in.value = 0    # No destination register for store
    dut.wb_mem_read.value = 0      
    dut.wb_mem_write.value = 1     # Memory write operation
    dut.wb_reg_write_in.value = 0  # No register write for store
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check memory control signals
    assert dut.mem_address.value == 0x2000, f"mem_address should be 0x2000, got {hex(dut.mem_address.value)}"
    assert dut.mem_read_en.value == 0, f"mem_read_en should be 0, got {dut.mem_read_en.value}"
    assert dut.mem_write_en.value == 1, f"mem_write_en should be 1, got {dut.mem_write_en.value}"
    assert dut.mem_write_data_out.value == 0x12345678, f"mem_write_data_out incorrect"
    
    # Check output signals
    assert dut.wb_reg_write_out.value == 0, f"wb_reg_write_out should be 0 for store, got {dut.wb_reg_write_out.value}"
    assert dut.wb_from_mem.value == 0, f"wb_from_mem should be 0 for store, got {dut.wb_from_mem.value}"

@cocotb.test
async def test_alu_result_passthrough(dut):
    """Test ALU result passes through when no memory operation"""
    
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset the module
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    
    # Set up an ALU operation (no memory access)
    dut.result_in.value = 0xDEADBEEF  # ALU result
    dut.mem_addr.value = 0
    dut.wb_rd_addr_in.value = 7       # Destination register
    dut.wb_mem_read.value = 0         # No memory read
    dut.wb_mem_write.value = 0        # No memory write
    dut.wb_reg_write_in.value = 1     # Will write result to register
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check memory control signals (should be inactive)
    assert dut.mem_read_en.value == 0, f"mem_read_en should be 0, got {dut.mem_read_en.value}"
    assert dut.mem_write_en.value == 0, f"mem_write_en should be 0, got {dut.mem_write_en.value}"
    
    # Check ALU result is correctly passed through
    assert dut.result_out.value == 0xDEADBEEF, f"result_out should be 0xDEADBEEF, got {hex(dut.result_out.value)}"
    assert dut.wb_rd_addr_out.value == 7, f"wb_rd_addr_out should be 7, got {dut.wb_rd_addr_out.value}"
    assert dut.wb_reg_write_out.value == 1, f"wb_reg_write_out should be 1, got {dut.wb_reg_write_out.value}"
    assert dut.wb_from_mem.value == 0, f"wb_from_mem should be 0 for ALU result, got {dut.wb_from_mem.value}"

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
    
    # Set initial values
    dut.result_in.value = 0x1000
    dut.wb_rd_addr_in.value = 5
    dut.wb_reg_write_in.value = 1
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Remember current values
    initial_result = dut.result_out.value
    initial_rd_addr = dut.wb_rd_addr_out.value
    
    # Now stall and change inputs
    dut.stall.value = 1
    dut.result_in.value = 0x2000
    dut.wb_rd_addr_in.value = 8
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # Check values didn't change despite new inputs
    assert dut.result_out.value == initial_result, f"result_out should not change during stall"
    assert dut.wb_rd_addr_out.value == initial_rd_addr, f"wb_rd_addr_out should not change during stall"
