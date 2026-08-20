import org.gradle.api.tasks.compile.JavaCompile

plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}

// Enforce Java 17 for every JavaCompile task in the Android project.
tasks.withType<JavaCompile>().configureEach {
    options.release.set(17)
}
