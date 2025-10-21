def iterate : (Nat → Nat) → Nat → (Nat → Nat)
  | _, 0 => id
  | f, n + 1 => f ∘ iterate f n

def step (n : Nat) :=
  if 2 ∣ n then
    n / 2
  else
    3 * n + 1

def CollatzConjecture := ∀ n > 0, ∃ i, iterate step i n = 1

opaque getFlag : CollatzConjecture → String := fun _ => "NNS{fake_flag}"

def userCode : String := "replace this"

-- The interpreter code will print out the value of `userCode`. You should only supply the code that will replace the string literal.
