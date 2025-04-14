import os
from pathlib import Path
from cocotb.runner import get_runner

sim = os.getenv("SIM", "icarus")
proj_path = Path("src/")

def run_alu_tests():
    sources = [proj_path / "xu/sky_alu.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_alu", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_alu", test_module="sky_alu_tb")

def run_register_file_tests():
    sources = [proj_path / "xu/sky_register_file.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_register_file", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_register_file", test_module="sky_register_file_tb")

if __name__ == "__main__":
    run_alu_tests()
    run_register_file_tests()
