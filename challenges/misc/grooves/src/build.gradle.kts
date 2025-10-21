plugins {
    kotlin("jvm") version "2.0.21"
    id("com.gradleup.shadow") version "9.0.0-beta6"
}

group = "no.nnsctf"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.apache.groovy:groovy-jsr223:4.0.25")
}

kotlin {
    jvmToolchain(11)
}

tasks {
    jar {
        manifest {
            attributes("Main-Class" to "no.nnsctf.grooves.GroovesKt")
        }
    }
}