package ru.kiracore.ai

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONObject
import ru.kiracore.ai.runtime.RuntimePhase
import ru.kiracore.ai.runtime.RuntimeSnapshot
import ru.kiracore.ai.security.AndroidSecureStore
import ru.kiracore.ai.storage.AndroidStorageProbe
import java.io.File
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

object KiraRuntimeBridge {
    private const val MODULE = "android_bridge"
    private const val EXPECTED_GENOME_REVISION = 22

    private val executor: ExecutorService = Executors.newSingleThreadExecutor {
        Thread(it, "KiraRuntime").apply { isDaemon = true }
    }
    private val listeners = CopyOnWriteArrayList<(RuntimeSnapshot) -> Unit>()

    @Volatile
    private var currentSnapshot = RuntimeSnapshot()

    fun snapshot(): RuntimeSnapshot = currentSnapshot

    fun subscribe(listener: (RuntimeSnapshot) -> Unit): AutoCloseable {
        listeners.add(listener)
        listener(currentSnapshot)
        return AutoCloseable { listeners.remove(listener) }
    }

    @Synchronized
    private fun python(context: Context): Python {
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(context.applicationContext))
        }
        return Python.getInstance()
    }

    private fun module(context: Context) =
        python(context).getModule(MODULE)

    private fun stageGenome(context: Context): File {
        val target = File(context.filesDir, "GENOME/genome.txt")
        target.parentFile?.mkdirs()
        context.assets.open("GENOME/genome.txt").use { input ->
            target.outputStream().use { output -> input.copyTo(output) }
        }
        return target
    }

    fun initializeAsync(context: Context) {
        if (currentSnapshot.phase == RuntimePhase.INITIALIZING ||
            currentSnapshot.phase == RuntimePhase.READY
        ) {
            return
        }

        publish(
            RuntimeSnapshot(
                phase = RuntimePhase.INITIALIZING,
                message = "Кира:Ядро инициализируется…",
            ),
        )

        val appContext = context.applicationContext
        executor.execute {
            try {
                stageGenome(appContext)
                val result = JSONObject(
                    module(appContext)
                        .callAttr("initialize", appContext.filesDir.absolutePath)
                        .toString(),
                )
                publish(
                    RuntimeSnapshot(
                        phase = RuntimePhase.READY,
                        message = "Кира:Ядро готово",
                        genomeRevision = result.optInt("genome_revision"),
                        genomeSha256 = result.optString("genome_sha256"),
                    ),
                )
            } catch (error: Throwable) {
                publish(
                    RuntimeSnapshot(
                        phase = RuntimePhase.FAILED,
                        message = "Ошибка запуска Кира:Ядра",
                        error = error.message ?: error::class.java.simpleName,
                    ),
                )
            }
        }
    }

    fun loadGenome(context: Context): JSONObject {
        ensureReady()
        return JSONObject(
            module(context.applicationContext)
                .callAttr("load_genome")
                .toString(),
        )
    }

    fun createSession(
        context: Context,
        provider: String,
        model: String,
        identityId: String? = null,
    ): JSONObject {
        ensureReady()
        val pyModule = module(context.applicationContext)
        val raw = if (identityId == null) {
            pyModule.callAttr("create_session", provider, model)
        } else {
            pyModule.callAttr("create_session", provider, model, identityId)
        }
        return JSONObject(raw.toString())
    }

    fun getRuntimeState(context: Context): JSONObject {
        ensureReady()
        return JSONObject(
            module(context.applicationContext)
                .callAttr("get_runtime_state")
                .toString(),
        )
    }

    fun runTestTurn(context: Context, sessionId: String, task: String): JSONObject {
        ensureReady()
        return JSONObject(
            module(context.applicationContext)
                .callAttr("run_test_turn", sessionId, task)
                .toString(),
        )
    }

    fun diagnostics(context: Context): JSONObject {
        val appContext = context.applicationContext
        val storage = AndroidStorageProbe(appContext)
        val secureStore = AndroidSecureStore(appContext)
        val result = JSONObject()
        result.put("application_id", BuildConfig.APPLICATION_ID)
        result.put("app_version", BuildConfig.VERSION_NAME)
        result.put("runtime_phase", currentSnapshot.phase.name)
        result.put("runtime_message", currentSnapshot.message)
        result.put("runtime_error", currentSnapshot.error)
        result.put("genome_revision", currentSnapshot.genomeRevision)
        result.put("genome_sha256", currentSnapshot.genomeSha256)
        result.put("storage_writable", storage.isWritable())
        result.put("storage_root", storage.rootPath())
        result.put("secure_store_available", secureStore.isAvailable())
        result.put(
            "providers",
            JSONObject()
                .put("OpenRouter", "цель A0/A1; подключение ещё не задано")
                .put("Gemini", "цель A0/A1; подключение ещё не задано"),
        )

        if (currentSnapshot.phase == RuntimePhase.READY) {
            val pythonDiagnostics = JSONObject(
                module(appContext).callAttr("diagnostics").toString(),
            )
            result.put("core_version", pythonDiagnostics.optString("core_version"))
            result.put("python_version", pythonDiagnostics.optString("python_version"))
        } else {
            result.put("core_version", JSONObject.NULL)
            result.put("python_version", JSONObject.NULL)
        }
        return result
    }

    fun health(context: Context): String {
        if (currentSnapshot.phase != RuntimePhase.READY) {
            return currentSnapshot.message
        }
        return module(context.applicationContext).callAttr("health").toString()
    }

    fun shutdown(context: Context) {
        if (currentSnapshot.phase == RuntimePhase.STOPPED) {
            return
        }
        publish(
            currentSnapshot.copy(
                phase = RuntimePhase.STOPPING,
                message = "Остановка Кира:Ядра…",
                error = null,
            ),
        )
        runCatching {
            module(context.applicationContext).callAttr("shutdown")
        }.also {
            publish(RuntimeSnapshot())
        }
    }

    private fun ensureReady() {
        check(currentSnapshot.phase == RuntimePhase.READY) {
            "Кира:Ядро ещё не готово."
        }
    }

    private fun publish(next: RuntimeSnapshot) {
        currentSnapshot = next
        listeners.forEach { listener ->
            runCatching { listener(next) }
        }
    }
}
