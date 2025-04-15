import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.binary import BinaryValue
from cocotb.handle import ModifiableObject

import random
import pytest

@cocotb.test
async def test_register_file_reset(dut) -> None:
    """Test register file reset functionality"""
    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # Set reset high
    dut.reset.value = 1
    
    # Wait a few clock cycles
    for _ in range(3):
        await Timer(1, units="ns")
    
    # Check that all registers read as 0
    for i in range(16):
        dut.read_addr1.value = i
        await RisingEdge(dut.clk)  
        assert dut.read_data1.value == 0, f"Register {i} not reset to 0"
    
    # De-assert reset
    dut.reset.value = 0
    await RisingEdge(dut.clk)

@cocotb.test
async def test_register_file_write_read(dut):
    """Test register file read/write ops"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    reg_values = {}
    for reg in range (1, 16):
        reg_val = random.randint(0, 0xFFFFFFFF)
        reg_values[reg] = reg_val

        dut.write_enable.value = 1
        dut.write_addr.value = reg
        dut.write_data.value = reg_val
        await RisingEdge(dut.clk)
    
    dut.write_enable.value = 0
    await RisingEdge(dut.clk)

    for reg in range (16):
        dut.read_addr1.value = reg
        await Timer(1, units="ns")

        expected = 0 if reg == 0 else reg_values[reg]
        assert dut.read_data1.value == expected, f"read1 from register {reg} failed: got {int(dut.read_data1.value)}, expected: {expected}"

        dut.read_addr2.value = reg
        await Timer(1, units="ns")
        assert dut.read_data2.value == expected, f"read2 from register {reg} failed: got {int(dut.read_data2.value)}, expected: {expected}"

@cocotb.test
async def test_zero_register(dut):
    """Tests that register 0 is hardwired to zero"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.reset.value = 1 
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    # attempt to write to reg 0
    dut.write_enable.value = 1
    dut.write_addr.value = 0
    dut.write_data.value = 0xDEADBEEF
    await RisingEdge(dut.clk)

    dut.write_enable.value = 0
    await RisingEdge(dut.clk)

    dut.read_addr1.value = 0
    await Timer(1, units="ns")

    assert dut.read_data1.value == 0, f"Register 0's value has been overwritten with {int(dut.read_data1.value)}"

@cocotb.test
async def test_simultaneous_reads(dut: ModifiableObject) -> None:
    """Test simultaneous reads from two different registers"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)
    
    # write different values to registers 1 and 2
    dut.write_enable.value = 1
    
    dut.write_addr.value = 1
    dut.write_data.value = 0xAAAAAAAA
    await RisingEdge(dut.clk)
    
    dut.write_addr.value = 2
    dut.write_data.value = 0x55555555
    await RisingEdge(dut.clk)
    
    # disable write
    dut.write_enable.value = 0
    await RisingEdge(dut.clk)
    
    # read simultaneously from both registers
    dut.read_addr1.value = 1
    dut.read_addr2.value = 2
    await Timer(1, units="ns")  # Wait for combinational read
    
    # verify both reads return correct values
    assert dut.read_data1.value == 0xAAAAAAAA, f"read1 failed: got {hex(int(dut.read_data1.value))} expected 0xAAAAAAAA"
    assert dut.read_data2.value == 0x55555555, f"read2 failed: got {hex(int(dut.read_data2.value))} expected 0x55555555"
    
    # try the other way around
    dut.read_addr1.value = 2
    dut.read_addr2.value = 1
    await Timer(1, units="ns")  # wait for combinational read
    
    # verify both reads return correct values
    assert dut.read_data1.value == 0x55555555, f"read1 failed: got {hex(int(dut.read_data1.value))} expected 0x55555555"
    assert dut.read_data2.value == 0xAAAAAAAA, f"read2 failed: got {hex(int(dut.read_data2.value))} expected 0xAAAAAAAA"
    

@cocotb.test
async def test_read_after_write(dut):
    """Test reading a value immediately after writing it"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.reset.value = 1 
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    # write value to reg 5
    dut.write_enable.value = 1
    dut.write_addr.value = 5
    dut.write_data.value  = 0x12345678

    # clock in write
    await RisingEdge(dut.clk)

    # disable write and read in same cycle
    dut.write_enable.value = 0
    dut.read_addr1.value = 5

    await Timer(1, units="ns") 

    assert dut.read_data1.value == 0x12345678, f"read-after-write failed: got {hex(dut.read_data1.value)}, expected: 0x12345678"
    



