// SeedEntry.java - pre-script for a raw LoG II import: ARM entry 0x080000C0 and Thumb main 0x08000158 only
// (the same two hard seeds codemap.py starts from), so the auto-analysis count is an independent shape.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import java.math.BigInteger;

public class SeedEntry extends GhidraScript {
    @Override
    public void run() throws Exception {
        Register tmode = currentProgram.getRegister("TMode");
        seed(0x080000C0L, 0, tmode);
        seed(0x08000158L, 1, tmode);
        println("seeded entry and main");
    }

    void seed(long at, int thumb, Register tmode) throws Exception {
        Address a = toAddr(at);
        currentProgram.getProgramContext().setValue(tmode, a, a, BigInteger.valueOf(thumb));
        addEntryPoint(a);
        disassemble(a);
        createFunction(a, null);
    }
}
