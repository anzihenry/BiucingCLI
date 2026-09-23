plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "{{PACKAGE_NAME}}.core.homestate"
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
    api(project(":core:model"))
    api(libs.kotlinx.coroutines.core)
    implementation(libs.dagger)
    annotationProcessor(libs.dagger.compiler)
    testImplementation(libs.junit4)
}
