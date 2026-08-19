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
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.10.0")
    implementation("androidx.compose.ui:ui:1.7.6")
    implementation("androidx.compose.material3:material3:1.3.1")
}
