// Decomp.java - post-script: decompile functions by name, one <out dir>\<name>.c each.
// Args: <out dir> <name> [<name> ...]. Run with -process -noanalysis -readOnly on the seeded project (README.md).
import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import java.io.*;
import java.util.List;

public class Decomp extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        DecompInterface ifc = new DecompInterface();
        DecompileOptions opts = new DecompileOptions();
        opts.grabFromProgram(currentProgram);
        opts.setRespectReadOnly(true);                                  // rom_code is read-only: pool loads fold to constants
        ifc.setOptions(opts);
        ifc.openProgram(currentProgram);
        println("rom_code write=" + currentProgram.getMemory().getBlock("rom_code").isWrite()
            + ", respect read-only=" + opts.isRespectReadOnly());
        for (int i = 1; i < args.length; i++) {
            List<Function> fs = getGlobalFunctions(args[i]);
            if (fs.size() != 1) {
                println(args[i] + ": " + fs.size() + " functions with this name, skipped");
                continue;
            }
            DecompileResults r = ifc.decompileFunction(fs.get(0), 120, monitor);
            if (!r.decompileCompleted()) {
                println(args[i] + ": decompile failed: " + r.getErrorMessage());
                continue;
            }
            try (PrintWriter w = new PrintWriter(new FileWriter(new File(args[0], args[i] + ".c")))) {
                w.print("// " + args[i] + " @ " + fs.get(0).getEntryPoint() + ", Ghidra 12.1.4 decompiler, seeded project\n");
                w.print(r.getDecompiledFunction().getC().replace("\r\n", "\n"));   // LF, as every LOG text file
            }
            println(args[i] + ": written");
        }
        ifc.dispose();
    }
}
