import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.binary import BinaryValue

@cocotb.test
async def test_fetch_stage_reset(dut):
    """Test that fetch stage resets properly"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # Check PC is reset to 0
    assert dut.pc.value == 0, f"PC was not reset to 0, got {dut.pc.value}"

    # Release reset
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    await RisingEdge(dut.clk)
    assert dut.pc_out.value == 0, f"First PC out should be 0, got {dut.pc_out.value}"
    assert dut.pc.value == 4, f"PC should increment to 4, got {dut.pc.value}"

@cocotb.test
async def test_fetch_instruction(dut):
    """Test that fetch stage retrieves instructions correctly"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Load test instructions into memory
    dut.instr_mem[0].value = 0x12345678
    dut.instr_mem[1].value = 0xAABBCCDD

    dut.reset.value = 1
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await RisingEdge(dut.clk)
    dut.reset.value = 0

    # First instruction should be fetched
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.instruction.value == 0x12345678, f"Expected 0x12345678, got {hex(dut.instruction.value)}"

    # Second instruction should be fetched
    await RisingEdge(dut.clk)
    assert dut.instruction.value == 0xAABBCCDD, f"Expected 0xAABBCCDD, got {hex(dut.instruction.value)}"

@cocotb.test
async def test_branch_taken(dut):
    """Test that branch target is used when branch is taken"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.instr_mem[0].value = 0x12345678
    dut.instr_mem[8].value = 0xAABBCCDD  # Instruction at address 32 (8 words)

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await RisingEdge(dut.clk)

    # Take a branch to address 32
    dut.branch_taken.value = 1
    dut.branch_target.value = 32

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    # PC should now be at branch target
    assert dut.pc.value == 32, f"PC should be 32 after branch, got {dut.pc.value}"
    assert dut.instruction.value == 0xAABBCCDD, f"Expected 0xAABBCCDD, got {hex(dut.instruction.value)}"

@cocotb.test
async def test_stall(dut):
    """Test that PC doesn't change when stalled"""

    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    dut.stall.value = 0
    dut.branch_taken.value = 0
    dut.branch_target.value = 0

    await RisingEdge(dut.clk)

    # Stall
    dut.stall.value = 1
    await RisingEdge(dut.clk)

    # Store current PC
    initial_pc = dut.pc.value

    # Check PC doesn't change over multiple cycles
    for _ in range(3):
        await RisingEdge(dut.clk)
        assert dut.pc.value == initial_pc, f"PC changed during stall"
