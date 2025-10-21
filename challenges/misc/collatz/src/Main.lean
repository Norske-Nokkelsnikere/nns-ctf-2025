import Lean
import Batteries.Data.String.Matcher

def runCode (code : String) : IO Lean.Environment := do
  Lean.initSearchPath <| ← Lean.findSysroot
  -- This is the wrong way to implement this but I'm too lazy to figure out how else to do it
  let .some env ← Lean.Elab.runFrontend code {} "Code.lean" `Code | throw <| IO.userError "runFrontend failed"
  return env

def scaryWords := #[
  "by_",     -- allows metaprogramming
  "run_",    -- allows metaprogramming
  "unsafe",  -- allows false proofs
  "axiom",   -- same
  "unsafe",  -- allows access to unsound stuff
  "\n",      -- scary
  "opaque",  -- scary
  "extern",  -- scary
  "Lean",    -- scary
  "IO",      -- scary
  "include", -- scary
]

def validate (code : String) : Bool := decide <| ¬∃ word ∈ scaryWords, code.containsSubstr word

def template := include_str "Template.lean"

def main : IO Unit := do
  println! "Please enter your code"
  let code := (← (← IO.getStdin).getLine).trim
  if !validate code then
    println! "Your code is too scary"
    return
  let flag := (← IO.getEnv "FLAG").getD "NNS{fake_flag}"
  let code := template |>.replace "NNS{fake_flag}" flag |>.replace "\"replace this\"" code

  let (_, val) ← IO.FS.withIsolatedStreams do
    let env ← runCode code
    let (_, s) := (Lean.CollectAxioms.collect `userCode).run env {}
    -- for obvious reasons we do not allow unsound axioms
    if ``sorryAx ∈ s.axioms then
      return .error "Cannot use `sorry"
    if ``Classical.choice ∈ s.axioms then
      return .error "Heresy"
    return unsafe env.evalConstCheck String {} ``String `userCode

  match val with
  | .ok x => println! "Your result was: {x}"
  | .error e => println! "There was an error: {e}"
