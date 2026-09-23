plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "{{PACKAGE_NAME}}.feature.home"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        minSdk = {{MIN_SDK}}
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
    implementation(project(":core:designsystem"))
    api(project(":core:homestate"))

    implementation(libs.androidx.compose.ui.tooling.preview)
    api(libs.kotlinx.coroutines.core)
    testImplementation(libs.junit4)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.material3)
}
