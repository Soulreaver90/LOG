// AnalyzerList.java - write every analysis option of the current program and its value, one "name = value" line,
// sorted. A probe for exact analyzer names before SeedSetup.java turns some off. Args: <out file>
import ghidra.app.script.GhidraScript;
import java.io.*;
import java.util.*;

public class AnalyzerList extends GhidraScript {
    @Override
    public void run() throws Exception {
        Map<String, String> opts = new TreeMap<>(getCurrentAnalysisOptionsAndValues(currentProgram));
        try (PrintWriter w = new PrintWriter(new FileWriter(getScriptArgs()[0]))) {
            for (Map.Entry<String, String> e : opts.entrySet()) {
                w.println(e.getKey() + " = " + e.getValue());
            }
        }
        println("options " + opts.size());
    }
}
