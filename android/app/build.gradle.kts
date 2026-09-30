import org.gradle.api.tasks.Copy

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("com.chaquo.python")
}

val syncGenome = tasks.register<Copy>("syncGenomeToAssets") {
    from(rootProject.layout.projectDirectory.dir("GENOME"))
    into(layout.projectDirectory.dir("src/main/assets/GENOME"))
}

tasks.named("preBuild").configure {
    dependsOn(syncGenome)
}

android {
    namespace = "ru.kiracore.ai"
    compileSdk = 37

    defaultConfig {
        applicationId = "ru.kiracore.ai"
        minSdk = 28
        targetSdk = 37
        versionCode = 1
        versionName = "0.1.0-alpha.1"

        ndk {
            abiFilters += listOf("arm64-v8a")
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

chaquopy {
    defaultConfig {
        version = "3.13"
    }
    sourceSets {
        getByName("main") {
            setSrcDirs(listOf(rootProject.layout.projectDirectory.dir("src").asFile))
        }
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2026.09.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)

    implementation("androidx.activity:activity-compose:1.13.0")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.11.0")
    implementation("androidx.core:core-ktx:1.17.0")

    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
}
