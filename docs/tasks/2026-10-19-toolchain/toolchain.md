# ARM toolchain and an assembler proof (approved 2026-10-19 8:40 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Read first: `docs\tasks\2026-10-18-disasm-study\disasm-study-report.md` (route A-lite and the install list), `scripts\permanent\log2_build.py`, `scripts\permanent\patches\ssj2_idle.py` (a hand-assembled Thumb hook) and one more patch with Thumb code.

## Final approval

I approved the Arm GNU Toolchain install for route A-lite: reassemble only the functions we change.

## Task 1: install, user scope, verified

- Download the current Arm GNU Toolchain for Windows, AArch32 bare-metal target (`arm-none-eabi`), the **zip** package (not the installer), only from `developer.arm.com`. Note the exact version and URL.
- Download its published SHA-256 checksum from the same page and verify the zip. If it does not match, delete the zip and stop.
- Download into a new empty folder `%USERPROFILE%\Tools\downloads\arm-gnu\`; unzip to `%USERPROFILE%\Tools\arm-gnu-toolchain-<version>\`. No admin rights, no PATH change, no registry change. Call the tools by absolute path.
- Run `arm-none-eabi-as --version`, `ld --version`, `objcopy --version` and report them.

## Task 2: a proof that it pays off

- Write the Thumb source of the `ssj2_idle` hook as a `.s` file in `scripts\one-time\2026-10-19-toolchain\ssj2_idle\`, assemble and link it at the address the patch uses, extract the raw bytes with `objcopy`, and compare with the bytes `ssj2_idle.py` writes in the r18 ROM. They must match byte for byte (labels and literal pools included). Explain any difference.
- Write `scripts\one-time\2026-10-19-toolchain\build_stub.py`: given a `.s` file and a load address, it returns the bytes (calls the toolchain by absolute path from a config value at the top). Test it on the same stub.
- Propose (do not apply) how a patch could use it: for example `apply()` assembling its stub at build time vs checking in the bytes with a test that the source still assembles to them. Say which you recommend and why, given that the build must stay reproducible without the toolchain on another machine.

## Parallel run

- Other tasks work in `scripts\permanent\` and `builds\`. Your files: the Tools folders above and `scripts\one-time\2026-10-19-toolchain\`. Do not edit any file in `scripts\permanent\`. Do not edit `docs\RE-BIBLE.md`; put bible rows in your report.

## Limits

- Install only the one zip above. Nothing else. Do not run anything from the download folder except the verified toolchain binaries after unzip.
- Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-19-toolchain\toolchain-report.md`: the version, URL and checksum result, the tool versions, the byte compare result, the helper and the recommendation. Then reply with status, the version, the compare result and concerns only.

