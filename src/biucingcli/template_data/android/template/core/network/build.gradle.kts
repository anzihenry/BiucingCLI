plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "{{PACKAGE_NAME}}.core.network"
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
}

dependencies {
    testImplementation(libs.junit4)
}
