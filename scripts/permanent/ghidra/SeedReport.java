// SeedReport.java - post-script: write every function Ghidra knows, one "0xADDR SIZE THUMB|ARM NAME" line, and
// count Error bookmarks (bad instructions, disassembly conflicts) per memory block: each one is a candidate wrong
// codemap start or mode. seeded_compare.py reads the function file. Args: <out file>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class SeedReport extends GhidraScript {
    @Override
    public void run() throws Exception {
        Register tmode = currentProgram.getRegister("TMode");
        int n = 0;
        try (PrintWriter w = new PrintWriter(new FileWriter(getScriptArgs()[0]))) {
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                BigInteger t = currentProgram.getProgramContext().getValue(tmode, f.getEntryPoint(), false);
                w.printf("0x%08x %d %s %s%n", f.getEntryPoint().getOffset(), f.getBody().getNumAddresses(),
                    t != null && t.intValue() == 1 ? "THUMB" : "ARM", f.getName());
                n++;
            }
        }
        println("functions " + n);
        Map<String, Integer> perBlock = new TreeMap<>();
        List<String> first = new ArrayList<>();
        Iterator<Bookmark> it = currentProgram.getBookmarkManager().getBookmarksIterator("Error");
        while (it.hasNext()) {
            Bookmark b = it.next();
            MemoryBlock blk = currentProgram.getMemory().getBlock(b.getAddress());
            perBlock.merge(blk == null ? "none" : blk.getName(), 1, Integer::sum);
            if (first.size() < 10) {
                first.add(b.getAddress() + " " + b.getCategory() + ": " + b.getComment());
            }
        }
        println("error bookmarks " + perBlock);
        for (String s : first) {
            println("  " + s);
        }
    }
}
