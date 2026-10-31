// FuncList.java - print every function start Ghidra knows, one "0xADDR SIZE THUMB|ARM" line, then a count.
// Run read-only on scratch\ghidra\LoG2.gpr through analyzeHeadless (see codemap_vs_ghidra.py). Args: <out file>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.*;
import java.io.*;
import java.math.BigInteger;

public class FuncList extends GhidraScript {
    @Override
    public void run() throws Exception {
        String out = getScriptArgs()[0];
        Register tmode = currentProgram.getRegister("TMode");
        int n = 0;
        try (PrintWriter w = new PrintWriter(new FileWriter(out))) {
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                BigInteger t = tmode == null ? null :
                    currentProgram.getProgramContext().getValue(tmode, f.getEntryPoint(), false);
                String mode = (t != null && t.intValue() == 1) ? "THUMB" : "ARM";
                w.printf("0x%08x %d %s%n", f.getEntryPoint().getOffset(), f.getBody().getNumAddresses(), mode);
                n++;
            }
        }
        println("functions " + n);
    }
}
