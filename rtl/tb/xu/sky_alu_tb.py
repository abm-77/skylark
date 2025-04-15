import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.binary import BinaryValue
from cocotb.handle import ModifiableObject

import random
import pytest

OP_ADD  = 0
OP_SUB  = 1
OP_AND  = 2
OP_OR   = 3
OP_XOR  = 4
OP_SLL  = 5
OP_SRL  = 6
OP_SRA  = 7
OP_SLT  = 8
OP_SLTU = 9
OP_MUL  = 10

async def reset_dut(dut):
    """Reset the DUT"""
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

@cocotb.test
async def test_alu_addition(dut: ModifiableObject):
    """Test ALU addition op"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)

    a = 0x12345678
    b = 0x87654321
    expected = (a + b) & 0xFFFFFFFF 

    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_ADD

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == expected, f"addition failed: got {int(dut.result.value)}, expected: {expected}"


@cocotb.test
async def test_alu_subtraction(dut):
    """Test ALU subtraction op"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)

    a = 0x12345678
    b = 0x87654321
    expected = (a - b) & 0xFFFFFFFF 

    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value= OP_SUB

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == expected, f"subtraction failed: got {int(dut.result.value)}, expected: {expected}"


@cocotb.test
async def test_alu_logical_ops(dut):
    """Test ALU logical ops"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)

    a = 0xAAAAAAAA
    b = 0x55555555

    # AND
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_AND

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (a & b), f"AND failed: got {int(dut.result.value)}, expected: {a & b}"

    # OR
    dut.operation.value = OP_OR
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (a | b), f"OR failed: got {int(dut.result.value)}, expected: {a | b}"

    # XOR
    dut.operation.value = OP_XOR
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (a ^ b), f"XOR failed: got {int(dut.result.value)}, expected: {a ^ b}"

@cocotb.test
async def test_alu_shifts(dut):
    """Test ALU shifts ops"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)

    a: int = 0x87654321
    shift = 4

    # SLL
    dut.operand_a.value = a
    dut.operand_b.value = shift
    dut.operation.value = OP_SLL
    expected = (a << shift) & 0xFFFFFFFF

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (expected), f"SLL failed: got {int(dut.result.value)}, expected: { expected }"

    # SRL
    dut.operation.value = OP_SRL
    expected = (a >> shift) & 0xFFFFFFFF

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (expected), f"SRL failed: got {int(dut.result.value)}, expected: { expected }"

    # SRA
    dut.operation.value = OP_SRA
    mask = (0xFFFFFFFF << (32 - shift)) & 0xFFFFFFFF
    expected = ((a >> shift) | mask) & 0xFFFFFFFF

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == (expected), f"SRA failed: got {int(dut.result.value)}, expected: { expected }"

@cocotb.test
async def test_alu_comparisons(dut):
    """Test ALU comparison ops"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    
    # Test SLT (set less than, signed)
    test_cases = [
        (10, 20, 1),         # Positive < Positive = True
        (20, 10, 0),         # Positive > Positive = False
        (-10, 10, 1),        # Negative < Positive = True
        (10, -10, 0),        # Positive > Negative = False
        (-20, -10, 1),       # Negative < Negative = True
        (-10, -20, 0)        # Negative > Negative = False
    ]
    for a, b, expected in test_cases:
        # Convert to 32-bit signed integers
        a_32bit = a & 0xFFFFFFFF
        b_32bit = b & 0xFFFFFFFF
        
        dut.operand_a.value = a_32bit
        dut.operand_b.value = b_32bit
        dut.operation.value = OP_SLT

        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        assert dut.result.value == expected, f"SLT failed for {a} < {b}: got {int(dut.result.value)} expected {expected}"
    
    # Test SLTU (set less than, unsigned)
    test_cases = [
        (10, 20, 1),              # 10 < 20 = True
        (20, 10, 0),              # 20 > 10 = False
        (0xFFFFFFFF, 1, 0),       # Max unsigned > 1 = False
        (1, 0xFFFFFFFF, 1)        # 1 < Max unsigned = True
    ]
    for a, b, expected in test_cases:
        dut.operand_a.value = a
        dut.operand_b.value = b
        dut.operation.value = OP_SLTU
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        assert dut.result.value == expected, f"SLTU failed for {a} < {b}: got {int(dut.result.value)} expected {expected}"
    
@cocotb.test
async def test_alu_multiplication(dut):
    """Test ALU multiplication op"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    
    a = 0x1234
    b = 0x5678
    expected = (a * b) & 0xFFFFFFFF  # Truncate to 32 bits
    
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_MUL
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.result.value == expected, f"Multiplication failed: got {int(dut.result.value)} expected {expected}"

@cocotb.test
async def test_alu_overflow(dut):
    """Test ALU overflow detection"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    
    # Test overflow on addition
    a = 0x7FFFFFFF  # Maximum positive 32-bit signed integer
    b = 1
    
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_ADD
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.overflow_flag.value == 1, f"overflow flag not set for addition overflow"
    
    # Test overflow on subtraction
    a = 0x80000000  # Minimum negative 32-bit signed integer
    b = 1
    
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_SUB
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.overflow_flag.value == 1, f"overflow flag not set for subtraction overflow"
    
    # Test no overflow case
    a = 0x10000000
    b = 0x10000000
    
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_ADD
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.overflow_flag.value == 0, f"overflow flag incorrectly set for non-overflow addition"

@cocotb.test
async def test_alu_zero_flag(dut):
    """Test ALU zero flag"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    
    # Test case where result is zero
    a = 0x12345678
    b = 0x12345678
    
    dut.operand_a.value = a
    dut.operand_b.value = b
    dut.operation.value = OP_SUB  # a - b = 0
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.zero_flag.value == 1, f"Zero flag not set when result is zero"
    
    # Test case where result is non-zero
    b = 0x12345677
    
    dut.operand_b.value = b
    
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.zero_flag.value == 0, f"Zero flag incorrectly set when result is non-zero"
    

@cocotb.test
async def test_alu_random_operations(dut):
    """Test ALU with random inputs and operations"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    
    def compute_expected(a, b, op):
        if op == OP_ADD:
            return (a + b) & 0xFFFFFFFF
        elif op == OP_SUB:
            return (a - b) & 0xFFFFFFFF
        elif op == OP_AND:
            return a & b
        elif op == OP_OR:
            return a | b
        elif op == OP_XOR:
            return a ^ b
        elif op == OP_SLL:
            return (a << (b & 0x1F)) & 0xFFFFFFFF
        elif op == OP_SRL:
            return (a >> (b & 0x1F)) & 0xFFFFFFFF
        elif op == OP_SRA:
            shift = b & 0x1F
            sign_bit = (a >> 31) & 1
            if sign_bit:
                mask = (0xFFFFFFFF << (32 - shift)) & 0xFFFFFFFF
                return ((a >> shift) | mask) & 0xFFFFFFFF
            else:
                return (a >> shift) & 0xFFFFFFFF
        elif op == OP_SLT:
            a_signed = a if a < 0x80000000 else a - 0x100000000
            b_signed = b if b < 0x80000000 else b - 0x100000000
            return 1 if a_signed < b_signed else 0
        elif op == OP_SLTU:
            return 1 if a < b else 0
        elif op == OP_MUL:
            return (a * b) & 0xFFFFFFFF
        else:
            return 0
    
    for _ in range(20):
        a = random.randint(0, 0xFFFFFFFF)
        b = random.randint(0, 0xFFFFFFFF)
        op = random.randint(0, 10)
        expected = compute_expected(a, b, op)
        
        dut.operand_a.value = a
        dut.operand_b.value = b
        dut.operation.value = op
        
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        assert dut.result.value == expected, f"Random test failed for op={op}, a=0x{a:08x}, b=0x{b:08x}: got 0x{int(dut.result.value):08x} expected 0x{expected:08x}"
    




