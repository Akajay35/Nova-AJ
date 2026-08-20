import org.gradle.api.tasks.compile.JavaCompile
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}

// Enforce Java 17 for every JavaCompile task in the Android project.
tasks.withType<JavaCompile>().configureEach {
    options.release.set(17)
}

// Diagnostic task: print the effective JVM targets that Gradle actually configures.
tasks.register("verifyJvmTargets") {
    doLast {
        println("=== Nova AJ JVM TARGET DIAGNOSTIC ===")
        println("Java home: ${System.getProperty("java.home")}")
        println("Java version: ${System.getProperty("java.version")}")
        tasks.withType<JavaCompile>().forEach {
            println("${it.path}: Java release=${it.options.release.orNull}")
        }
        tasks.withType<KotlinCompile>().forEach {
            println("${it.path}: Kotlin jvmTarget=${it.compilerOptions.jvmTarget.orNull}")
        }
        println("=== END JVM TARGET DIAGNOSTIC ===")
    }
}
