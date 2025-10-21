import Lake

open System Lake DSL

package «collatz» where version := v!"0.1.0"

require "leanprover-community" / "batteries" @ git "main"

@[default_target] lean_exe «collatz» where
  root := `Main
  supportInterpreter := true
