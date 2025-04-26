import cocotb
from cocotb.triggers import Timer

@cocotb.test
async def test_alu_result_writeback(dut):
    """Test writeback of ALU result to register file"""
    
    # Set up ALU result writeback
    dut.result_in.value = 0xDEADBEEF  # ALU result
    dut.mem_data.value = 0x12345678   # Memory data (shouldn't be used)
    dut.wb_rd_addr.value = 7          # Destination register
    dut.wb_reg_write.value = 1        # Enable register write
    dut.wb_from_mem.value = 0         # Select ALU result, not memory data
    
    # No clock needed as writeback stage is combinational
    await Timer(1, units="ns")
    
    # Check register file control signals
    assert dut.rf_write_enable.value == 1, f"rf_write_enable should be 1, got {dut.rf_write_enable.value}"
    assert dut.rf_write_addr.value == 7, f"rf_write_addr should be 7, got {dut.rf_write_addr.value}"
    assert dut.rf_write_data.value == 0xDEADBEEF, f"rf_write_data should be ALU result 0xDEADBEEF, got {hex(dut.rf_write_data.value)}"

@cocotb.test
async def test_memory_data_writeback(dut):
    """Test writeback of memory data to register file"""
    
    # Set up memory data writeback
    dut.result_in.value = 0xDEADBEEF  # ALU result (shouldn't be used)
    dut.mem_data.value = 0x12345678   # Memory data
    dut.wb_rd_addr.value = 5          # Destination register
    dut.wb_reg_write.value = 1        # Enable register write
    dut.wb_from_mem.value = 1         # Select memory data, not ALU result
    
    await Timer(1, units="ns")
    
    # Check register file control signals
    assert dut.rf_write_enable.value == 1, f"rf_write_enable should be 1, got {dut.rf_write_enable.value}"
    assert dut.rf_write_addr.value == 5, f"rf_write_addr should be 5, got {dut.rf_write_addr.value}"
    assert dut.rf_write_data.value == 0x12345678, f"rf_write_data should be memory data 0x12345678, got {hex(dut.rf_write_data.value)}"

@cocotb.test
async def test_write_disabled(dut):
    """Test that writes are disabled when wb_reg_write is 0"""
    
    # Set up no register write
    dut.result_in.value = 0xDEADBEEF
    dut.wb_rd_addr.value = 3
    dut.wb_reg_write.value = 0        # Disable register write
    
    await Timer(1, units="ns")
    
    # Check register file control signals
    assert dut.rf_write_enable.value == 0, f"rf_write_enable should be 0, got {dut.rf_write_enable.value}"
