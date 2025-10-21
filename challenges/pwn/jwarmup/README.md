
```
java -jar jol-cli-0.17-full.jar internals java.lang.String
# WARNING: Unable to attach Serviceability Agent. You can try again with escalated privileges. Two options: a) use -Djol.tryWithSudo=true to try with sudo; b) echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
# VM mode: 64 bits
# Compressed references (oops): 3-bit shift
# Compressed class pointers: 3-bit shift
# WARNING | Compressed references base/shifts are guessed by the experiment!
# WARNING | Therefore, computed addresses are just guesses, and ARE NOT RELIABLE.
# WARNING | Make sure to attach Serviceability Agent to get the reliable addresses.
# Object alignment: 8 bytes
#                       ref, bool, byte, char, shrt,  int,  flt,  lng,  dbl
# Field sizes:            4,    1,    1,    2,    2,    4,    4,    8,    8
# Array element sizes:    4,    1,    1,    2,    2,    4,    4,    8,    8
# Array base offsets:    16,   16,   16,   16,   16,   16,   16,   16,   16

Instantiated the sample instance via default constructor.

java.lang.String object internals:
OFF  SZ      TYPE DESCRIPTION               VALUE
  0   8           (object header: mark)     0x0000000000000001 (non-biasable; age: 0)
  8   4           (object header: class)    0x0000fa78
 12   4       int String.hash               0
 16   1      byte String.coder              0
 17   1   boolean String.hashIsZero         false
 18   2           (alignment/padding gap)
 20   4    byte[] String.value              []
Instance size: 24 bytes
Space losses: 2 bytes internal + 0 bytes external = 2 bytes total
```

https://github.com/openjdk/jdk/blob/890adb6410dab4606a4f26a942aed02fb2f55387/src/hotspot/share/oops/arrayOop.hpp#L35-L39

```
// The layout of array Oops is:
//
//  markWord
//  Klass*    // 32 bits if compressed but declared 64 in LP64.
//  length    // shares klass memory or allocated after declared fields.
```