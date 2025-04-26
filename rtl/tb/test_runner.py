import os
from pathlib import Path
from cocotb.runner import get_runner

sim = os.getenv("SIM", "icarus")
proj_path = Path("src/")

def run_alu_tests():
    sources = [proj_path / "xu/sky_alu.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_alu", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_alu", test_module="xu.sky_alu_tb")

def run_register_file_tests():
    sources = [proj_path / "xu/sky_register_file.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_register_file", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_register_file", test_module="xu.sky_register_file_tb")

def run_xu_pipeline_tests():
    sources = [proj_path / "xu/pipeline/sky_fetch_stage.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_fetch_stage", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_fetch_stage", test_module="xu.sky_xu_fetch_stage_tb")

    sources = [proj_path / "xu/pipeline/sky_decode_stage.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_decode_stage", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_decode_stage", test_module="xu.sky_xu_decode_stage_tb")

    sources = [proj_path / "xu/pipeline/sky_execute_stage.sv"]
    runner = get_runner(sim)
    runner.build(sources=sources, hdl_toplevel="sky_execute_stage", always=True, timescale=("1ns", "1ns"))
    runner.test(hdl_toplevel="sky_execute_stage", test_module="xu.sky_xu_execute_stage_tb")

if __name__ == "__main__":
    run_alu_tests()
    run_register_file_tests()
    run_xu_pipeline_tests()
