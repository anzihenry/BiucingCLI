pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }

// Every Gradle invocation (including Android Studio) verifies the resolved binary closure.
val verifyArgs = mutableListOf("python3", "scripts/components", "verify")
if (gradle.startParameter.taskNames.any { it.contains("release", ignoreCase = true) }) verifyArgs.add("--release")
val verification = ProcessBuilder(verifyArgs).directory(settingsDir).inheritIO().start()
check(verification.waitFor() == 0) { "Component verification failed. Run make components-bootstrap or scripts/components resolve." }

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        exclusiveContent {
            forRepository { maven { url = uri(".build/components/maven") } }
            filter { includeGroup("{{PACKAGE_NAME}}.components") }
        }
        google()
        mavenCentral()
    }
}
rootProject.name = "{{PROJECT_NAME}}"
include(":app")
include(":wear")
include(":tv")
