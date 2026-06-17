plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

import java.util.Properties

fun loadLocalProperties(rootDir: java.io.File): Properties {
    val properties = Properties()
    val localPropertiesFile = rootDir.resolve("local.properties")

    if (localPropertiesFile.isFile) {
        localPropertiesFile.inputStream().use(properties::load)
    }

    return properties
}

fun Project.releaseProperty(
    localProperties: Properties,
    gradleKey: String,
    envKey: String,
): String? {
    return providers.gradleProperty(gradleKey).orNull
        ?: localProperties.getProperty(gradleKey)
        ?: System.getenv(envKey)
}

val localProperties = loadLocalProperties(rootDir)
val releaseStoreFile = project.releaseProperty(
    localProperties,
    "biucing.release.storeFile",
    "BIUCING_RELEASE_STORE_FILE",
)
val releaseStorePassword = project.releaseProperty(
    localProperties,
    "biucing.release.storePassword",
    "BIUCING_RELEASE_STORE_PASSWORD",
)
val releaseKeyAlias = project.releaseProperty(
    localProperties,
    "biucing.release.keyAlias",
    "BIUCING_RELEASE_KEY_ALIAS",
)
val releaseKeyPassword = project.releaseProperty(
    localProperties,
    "biucing.release.keyPassword",
    "BIUCING_RELEASE_KEY_PASSWORD",
)
val hasCompleteReleaseSigning =
    listOf(
        releaseStoreFile,
        releaseStorePassword,
        releaseKeyAlias,
        releaseKeyPassword,
    ).all { !it.isNullOrBlank() }

android {
    namespace = "{{ANDROID_NAMESPACE}}"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        applicationId = "{{APPLICATION_ID}}"
        minSdk = {{MIN_SDK}}
        targetSdk = {{TARGET_SDK}}
        versionCode = {{VERSION_CODE}}
        versionName = "{{VERSION_NAME}}"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }

        release {
            isMinifyEnabled = false
            if (hasCompleteReleaseSigning) {
                signingConfig = signingConfigs.getByName("release")
            }
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    signingConfigs {
        create("release") {
            if (hasCompleteReleaseSigning) {
                storeFile = file(releaseStoreFile!!)
                storePassword = releaseStorePassword
                keyAlias = releaseKeyAlias
                keyPassword = releaseKeyPassword
            }
        }
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
    implementation(project(":core:model"))
    implementation(project(":core:designsystem"))
    implementation(project(":core:network"))
    implementation(project(":feature:home"))
    implementation(project(":feature:settings"))

    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.google.material)

    testImplementation(libs.junit4)
    testImplementation(project(":core:testing"))
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.test.ext.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}
