# E(x)ecution (U)nit - XU

The skylark execution unit (XU) is an instance of a singular processing element. It consists of an 
ALU and a register file and implements a traditional 5-stage RISC pipeline.

## Fetch
The fetch stage is very simple: if a branch was taken, the PC will be set to the branch target.
Otherwise, the PC will increment by 4 (bytes).

## Decode
Instructions in our made up ISA are encoded as follows
- bits 31-28: opcode
- bits 27-23: source register 1
- bits 23-20: source register 2
- bits 19-15: destination register
- bits 15-12: funct encoding
- bits 11-0:  immediate value

The opcodes can be translated to:
- 0000: r(egister)-type instruction
- 0001: i(mmediate)-type instruction
- 0010: load instruction
- 0011: store instruction

The decode stage also checks to see if data will be forwarded from the writeback stage for use in the 
current instruction. 

# Execute Stage
The execute stage simply forwards decoded instructions to the ALU and any results that need to be written to memory 
to the memory stage.
