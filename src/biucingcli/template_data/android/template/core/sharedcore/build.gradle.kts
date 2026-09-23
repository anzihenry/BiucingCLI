plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "{{PACKAGE_NAME}}.core.sharedcore"
    compileSdk = {{COMPILE_SDK}}
    ndkVersion = "28.2.13676358"
    externalNativeBuild { cmake { path = file("src/main/cpp/CMakeLists.txt"); version = "3.22.1" } }

    defaultConfig {
        minSdk = {{MIN_SDK}}
        ndk { abiFilters += listOf("arm64-v8a", "x86_64") }
        externalNativeBuild { cmake { arguments += "-DANDROID_STL=c++_static" } }
        consumerProguardFiles("consumer-rules.pro")
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
    api(libs.kotlinx.coroutines.core)
    testImplementation(libs.junit4)
}

android.testOptions.unitTests.all {
    val nativePath = providers.gradleProperty("hostNativePath").orNull
    if (nativePath != null) it.jvmArgs("-Djava.library.path=$nativePath")
    else it.exclude("**/CoreSessionTest.class")
}
