import com.android.build.gradle.LibraryExtension
import groovy.json.JsonSlurper
import com.diffplug.gradle.spotless.SpotlessExtension

plugins {
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.spotless)
}
val declaration = JsonSlurper().parse(file("../dependencies/components.json")) as Map<*, *>
val versions = declaration["components"] as Map<*, *>
subprojects {
    if (!versions.containsKey(name)) return@subprojects
    group = "{{PACKAGE_NAME}}.components"
    version = if (name == providers.gradleProperty("componentName").orNull)
        providers.gradleProperty("componentVersion").get() else versions[name].toString()
    apply(plugin = "maven-publish")
    apply(plugin = "com.diffplug.spotless")
    extensions.configure<SpotlessExtension> {
        kotlin { target("src/**/*.kt"); ktlint(libs.versions.ktlint.get()) }
        kotlinGradle { target("*.gradle.kts"); ktlint(libs.versions.ktlint.get()) }
    }
    plugins.withId("com.android.library") {
        extensions.configure<LibraryExtension> {
            publishing { singleVariant("release") { withSourcesJar() } }
        }
    }
    val sdkProject = this
    gradle.projectsEvaluated {
        sdkProject.extensions.configure<PublishingExtension> {
            publications {
                create<MavenPublication>("release") {
                    from(sdkProject.components["release"])
                    artifactId = sdkProject.name
                }
            }
            repositories {
                maven {
                    name = "Components"
                    url = uri(providers.gradleProperty("componentRepository").getOrElse("../.artifacts/staging"))
                }
            }
        }
    }
    dependencyLocking {
        lockAllConfigurations()
        lockMode.set(LockMode.STRICT)
    }
}
