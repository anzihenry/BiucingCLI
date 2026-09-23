pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
    versionCatalogs { create("libs") { from(files("../gradle/libs.versions.toml")) } }
}
rootProject.name = "{{PROJECT_NAME}}-components"
listOf("model", "designsystem", "network", "testing", "sharedcore").forEach {
    include(":core:$it")
    project(":core:$it").projectDir = file("../core/$it")
}
listOf("home", "settings").forEach {
    include(":feature:$it")
    project(":feature:$it").projectDir = file("../feature/$it")
}
