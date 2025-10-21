package no.nnsctf.grooves

import groovy.lang.GroovyClassLoader
import org.codehaus.groovy.control.CompilerConfiguration
import org.codehaus.groovy.jsr223.GroovyScriptEngineImpl

val naughtyStrings = setOf(
    "cat",
    "bash",
    "flag",
    "Class",
    "concat",
    "get",
    "set",
    "exec",
    "Process",
    "eval",
    "+",
    "$",
    "{",
    "}",
    "\"",
    "'"
)

fun main() {
    println("Did you know that Vikingskipet was built for the Ice Skating competition of the Winter Olympics 1994?")
    print("Send your grooves: ")
    val input = readln()

    if (input.length > 340) {
        println("Too many grooves!")
        return
    }

    if (naughtyStrings.any { input.contains(it) }) {
        println("Naughty!")
        return
    }

    val classLoader = Thread.currentThread().contextClassLoader
    val jailClassLoader = JailClassLoader(classLoader)
    val compilerConfiguration = CompilerConfiguration(CompilerConfiguration.DEFAULT)
    val groovyClassLoader = GroovyClassLoader(jailClassLoader, compilerConfiguration)
    val engine = GroovyScriptEngineImpl(groovyClassLoader)

    System.setSecurityManager(JailSecurityManager())
    try {
        println(engine.eval(input))
    } catch (e: Exception) {
        println("Bad code! Your grooves resulted in '${e.message}'")
    }
}
