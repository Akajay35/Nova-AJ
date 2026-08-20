import org.gradle.api.tasks.compile.JavaCompile
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.novaj"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.novaj"
        minSdk = 26
        targetSdk = 35
        versionCode = 286
        versionName = "0.286.0"

        val apiUrl = providers.gradleProperty("novaApiUrl").orElse("http://10.0.2.2:8080").get()
        val apiToken = providers.gradleProperty("novaApiToken").orElse("").get()
        buildConfigField("String", "NOVA_API_URL", "\"${apiUrl.replace("\"", "\\\"")}\"")
        buildConfigField("String", "NOVA_API_TOKEN", "\"${apiToken.replace("\"", "\\\"")}\"")
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// Force every Java compile task in the app module to target JVM 17.
tasks.withType<JavaCompile>().configureEach {
    sourceCompatibility = "17"
    targetCompatibility = "17"
    options.release.set(17)
}

// Force every Kotlin compile task in the app module to target JVM 17.
tasks.withType<KotlinCompile>().configureEach {
    compilerOptions.jvmTarget.set(JvmTarget.JVM_17)
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.10.0")
    implementation("androidx.compose.ui:ui:1.7.6")
    implementation("androidx.compose.material3:material3:1.3.1")
}
