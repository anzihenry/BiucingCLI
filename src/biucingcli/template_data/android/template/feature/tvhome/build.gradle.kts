plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "{{PACKAGE_NAME}}.feature.tvhome"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        minSdk = maxOf(23, {{MIN_SDK}})
    }

    compileOptions {
        sourceCompatibility = JavaVersion.toVersion("{{JAVA_VERSION}}")
        targetCompatibility = JavaVersion.toVersion("{{JAVA_VERSION}}")
    }

    kotlinOptions {
        jvmTarget = "{{JAVA_VERSION}}"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    api(project(":core:network"))
    api(project(":core:homestate"))

    implementation(libs.androidx.compose.ui.tooling.preview)
    api(libs.kotlinx.coroutines.core)
    testImplementation(libs.junit4)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.tv.material)
}
