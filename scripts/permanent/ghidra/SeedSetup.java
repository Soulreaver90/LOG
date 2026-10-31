// SeedSetup.java - pre-script for a raw LoG II USA import: memory map, analyzer options, codemap starts and names.
// Args: <codemap.json> <symbols.json> (scripts\permanent\disasm\data\). Run before auto-analysis (see README.md).
//  1. Memory: splits the ROM at code_hi into rom_code (r-x) and rom_data (r--, so no analyzer decodes it as
//     code); adds iwram_code (the crt0 copy of rom:0x7FD6BC, bible s14 #boot), iwram, ewram and io.
//  2. Analyzers: turns off the ones that search data for code (the study saw 2,353 false functions).
//  3. Seeds: every codemap start with its mode (TMode 1 = Thumb, 0 = ARM), then its symbols.json name and
//     bible tag; table, vtable and ram symbols become labels.
import com.google.gson.*;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.SourceType;
import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class SeedSetup extends GhidraScript {
    static final long ROM_BASE = 0x08000000L;
    static final String[] OFF = {
        "Function Start Pre Search", "Function Start Search", "Function Start Search After Code",
        "Function Start Search After Data", "Create Address Tables", "Embedded Media",
        "ARM Aggressive Instruction Finder", "Aggressive Instruction Finder"};

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        JsonObject cm = JsonParser.parseReader(new FileReader(args[0])).getAsJsonObject();
        JsonArray syms = JsonParser.parseReader(new FileReader(args[1])).getAsJsonArray();
        memory(cm);
        for (String name : OFF) {
            setAnalysisOption(currentProgram, name, "false");
        }
        println("analyzers off: " + String.join(", ", OFF));
        seed(cm, syms);
    }

    // ===== memory map =====
    void memory(JsonObject cm) throws Exception {
        Memory mem = currentProgram.getMemory();
        Address codeHi = toAddr(cm.get("code_hi").getAsLong());
        mem.split(mem.getBlock(toAddr(ROM_BASE)), codeHi);
        perms(mem.getBlock(toAddr(ROM_BASE)), "rom_code", false, true);
        perms(mem.getBlock(codeHi), "rom_data", false, false);
        JsonArray iw = cm.getAsJsonArray("iwram");                     // [rom offset, 0x03000000, size]
        long src = iw.get(0).getAsLong(), dst = iw.get(1).getAsLong(), size = iw.get(2).getAsLong();
        byte[] code = new byte[(int) size];
        mem.getBytes(toAddr(ROM_BASE + src), code);
        perms(mem.createInitializedBlock("iwram_code", toAddr(dst), new ByteArrayInputStream(code), size, monitor, false),
            "iwram_code", true, true);
        perms(mem.createUninitializedBlock("iwram", toAddr(dst + size), 0x03008000L - dst - size, false), "iwram", true, false);
        perms(mem.createUninitializedBlock("ewram", toAddr(0x02000000L), 0x40000, false), "ewram", true, false);
        MemoryBlock io = mem.createUninitializedBlock("io", toAddr(0x04000000L), 0x400, false);
        perms(io, "io", true, false);
        io.setVolatile(true);
        println(String.format("memory: rom_code to %s, iwram_code 0x%x bytes from rom:0x%x", codeHi, size, src));
    }

    void perms(MemoryBlock b, String name, boolean write, boolean exec) throws Exception {
        b.setName(name);
        b.setRead(true);
        b.setWrite(write);
        b.setExecute(exec);
    }

    // ===== starts, names, labels =====
    void seed(JsonObject cm, JsonArray syms) throws Exception {
        Map<Long, String[]> names = new HashMap<>();                   // address -> {name, kind, bible}
        for (JsonElement e : syms) {
            JsonObject o = e.getAsJsonObject();
            names.put(Long.decode(o.get("address").getAsString()),
                new String[] {o.get("name").getAsString(), o.get("kind").getAsString(), o.get("bible").getAsString()});
        }
        Register tmode = currentProgram.getRegister("TMode");
        TreeMap<Long, String> starts = new TreeMap<>();
        for (Map.Entry<String, JsonElement> e : cm.getAsJsonObject("functions").entrySet()) {
            starts.put(Long.decode(e.getKey()), e.getValue().getAsJsonArray().get(0).getAsString());
        }
        for (Map.Entry<Long, String> s : starts.entrySet()) {      // context first, so no flow decodes a start in the wrong mode
            Address a = toAddr(s.getKey());
            currentProgram.getProgramContext().setValue(tmode, a, a, BigInteger.valueOf(s.getValue().equals("T") ? 1 : 0));
        }
        for (Long at : starts.keySet()) {
            disassemble(toAddr(at));
        }
        int made = 0, named = 0, failed = 0;
        for (Long at : starts.keySet()) {
            Address a = toAddr(at);
            String[] n = names.get(at);
            Function f = getFunctionAt(a) != null ? getFunctionAt(a) : createFunction(a, null);
            if (f == null) {
                failed++;
                println(String.format("createFunction failed at 0x%08x", at));
                continue;
            }
            made++;
            if (n != null && n[1].equals("func")) {
                f.setName(n[0], SourceType.USER_DEFINED);
                setPlateComment(a, n[0] + "  (bible " + (n[2].isEmpty() ? "no row" : n[2]) + ")");
                named++;
            }
        }
        for (Long at : starts.keySet()) {                             // bodies stop at every start, now all exist
            Function f = getFunctionAt(toAddr(at));
            if (f != null) {
                CreateFunctionCmd.fixupFunctionBody(currentProgram, f, monitor);
            }
        }
        int labels = 0;
        for (Map.Entry<Long, String[]> e : names.entrySet()) {
            Address a = toAddr(e.getKey());
            if (!e.getValue()[1].equals("func") && currentProgram.getMemory().contains(a)) {
                createLabel(a, e.getValue()[0], true, SourceType.USER_DEFINED);
                labels++;
            }
        }
        println(String.format("seeded: %d starts, %d functions, %d failed, %d named, %d labels",
            starts.size(), made, failed, named, labels));
    }
}
