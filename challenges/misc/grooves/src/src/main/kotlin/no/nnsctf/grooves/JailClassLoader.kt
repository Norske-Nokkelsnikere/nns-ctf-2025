package no.nnsctf.grooves

class JailClassLoader(private val parent: ClassLoader) : ClassLoader() {
    private val allowedClasses = setOf(
        "groovy.grape.GrabAnnotationTransformation",
        "groovy.lang.Script",
        "groovy.lang.Binding",
        "groovy.lang.MetaClass",
        "groovy.lang.GroovyObject",
        "java.lang.String",
        "java.lang.Object",
        "java.lang.Integer",
        "java.lang.invoke.MethodHandles\$Lookup",
        "org.codehaus.groovy.reflection.ClassInfo",
        "org.codehaus.groovy.runtime.ScriptBytecodeAdapter",
        "org.codehaus.groovy.vmplugin.v8.IndyInterface",
        "Script1BeanInfo",
        "Script1Customizer",
    )

    override fun loadClass(name: String, resolve: Boolean): Class<*>? {
        if (name in allowedClasses)
            return parent.loadClass(name)

        return null
    }
}