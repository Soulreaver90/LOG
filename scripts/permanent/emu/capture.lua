-- capture.lua - The Lua side of the capture loop. capture.py writes run.lua, which sets CAPTURE_DIR and
--               CAPTURE_SPEED and then runs this file.
--
-- Reads:   <CAPTURE_DIR>steps.txt, one step a line, forward slashes:
--            wait <frames> | press <button> <frames> | shot <name> | read <addr> <width> <label>
--            savestate <path> | end
-- Writes:  <CAPTURE_DIR>result.txt, one line a step: <index> <frame> <kind> <detail>.
--          A read wider than 8 bytes goes to <CAPTURE_DIR><label>.bin and the line names the file.
--          Screenshots go to <CAPTURE_DIR>shots/<name>.png.
-- Why a file: console.log does not reach stdout under --chromeless, so result.txt is the only channel.
-- Every path ends at client.exit(), so a fault never waits for the wrapper timeout.

local DIR = CAPTURE_DIR
local SPEED = CAPTURE_SPEED or 100
local INLINE = 8

local out = io.open(DIR .. "result.txt", "wb")

local function say(text)
  out:write(text .. "\n")
  out:flush()
end

local function hex(bytes)
  local parts = {}
  for i = 1, #bytes do parts[i] = string.format("%02x", bytes[i]) end
  return table.concat(parts)
end

-- ===== memory =====
local function set_domain()
  local ok, err = pcall(function() memory.usememorydomain("System Bus") end)
  say("# domain System Bus ok=" .. tostring(ok) .. " err=" .. tostring(err))
end

-- A missing byte is an error, never a substitute: a silent 0 would read as real memory.
local function read_bytes(addr, width)
  local ok, arr = pcall(function() return memory.read_bytes_as_array(addr, width) end)
  local bytes = {}
  if ok and arr then
    for i = 1, width do
      if arr[i] == nil then
        error(string.format("read_bytes_as_array gave no byte %d of %d at 0x%08X", i, width, addr))
      end
      bytes[i] = arr[i]
    end
    return bytes
  end
  for i = 1, width do bytes[i] = memory.read_u8(addr + i - 1) end
  return bytes
end

-- ===== steps =====
local function split(line)
  local words = {}
  for word in string.gmatch(line, "%S+") do words[#words + 1] = word end
  return words
end

local function load_steps()
  local steps = {}
  for line in io.lines(DIR .. "steps.txt") do
    local words = split(line)
    if #words > 0 then steps[#steps + 1] = words end
  end
  return steps
end

local function do_wait(frames)
  for _ = 1, frames do emu.frameadvance() end
end

-- The GBA core has one controller and no "P1 " prefix: joypad.get(1) is empty, so joypad.set(t, 1) sets
-- nothing and the game never sees the button. Always call joypad.set with no controller number.
local function do_press(button, frames)
  for _ = 1, frames do
    joypad.set({ [button] = true })
    emu.frameadvance()
  end
end

local function do_read(index, addr, width, label)
  local bytes = read_bytes(addr, width)
  if width <= INLINE then
    say(string.format("%d %d read %s 0x%08X %s", index, emu.framecount(), label, addr, hex(bytes)))
    return
  end
  local bin = io.open(DIR .. label .. ".bin", "wb")
  local chunk = {}
  for i = 1, width do
    chunk[#chunk + 1] = string.char(bytes[i])
    if #chunk == 4096 then
      bin:write(table.concat(chunk))
      chunk = {}
    end
  end
  bin:write(table.concat(chunk))
  bin:close()
  say(string.format("%d %d read %s 0x%08X file:%s.bin:%d", index, emu.framecount(), label, addr, label, width))
end

local function run_step(index, words)
  local kind = words[1]
  if kind == "wait" then
    do_wait(tonumber(words[2]))
    say(string.format("%d %d wait %s", index, emu.framecount(), words[2]))
  elseif kind == "press" then
    do_press(words[2], tonumber(words[3]))
    say(string.format("%d %d press %s %s", index, emu.framecount(), words[2], words[3]))
  elseif kind == "shot" then
    client.screenshot(DIR .. "shots/" .. words[2] .. ".png")
    say(string.format("%d %d shot %s shots/%s.png", index, emu.framecount(), words[2], words[2]))
  elseif kind == "read" then
    do_read(index, tonumber(words[2]), tonumber(words[3]), words[4])
  elseif kind == "savestate" then
    savestate.save(words[2])
    say(string.format("%d %d savestate %s", index, emu.framecount(), words[2]))
  elseif kind == "end" then
    say(string.format("%d %d end", index, emu.framecount()))
  else
    error("unknown step: " .. tostring(kind))
  end
end

-- ===== the run =====
local started = os.clock()
local first_frame = 0

local ok, err = pcall(function()
  pcall(function() client.speedmode(SPEED) end)
  pcall(function() client.unthrottle() end)
  pcall(function() client.SetSoundOn(false) end)
  say("# speed " .. tostring(SPEED))
  set_domain()
  first_frame = emu.framecount()
  local steps = load_steps()
  for index = 1, #steps do run_step(index, steps[index]) end
end)

if not ok then say("# error " .. tostring(err)) end

local seconds = os.clock() - started
local frames = emu.framecount() - first_frame
say(string.format("# frames %d seconds %.2f fps %.1f", frames, seconds,
  (seconds > 0) and (frames / seconds) or 0))
say("# done ok=" .. tostring(ok))
out:close()
client.exit()
