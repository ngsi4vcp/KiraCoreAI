package ru.kiracore.ai

import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.json.JSONArray
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
        var roomPersistence: ru.kiracore.ai.storage.room.AndroidRoomPersistenceGateway? = null
        executor.execute {
            try {
                stageGenome(appContext)
                roomPersistence =
                    ru.kiracore.ai.storage.room.AndroidRoomPersistenceGateway(appContext)
                val result = JSONObject(
                    module(appContext)
                        .callAttr(
                            "initialize",
                            appContext.filesDir.absolutePath,
                            roomPersistence,
                        )
                        .toString(),
                )
                val runtimeState = JSONObject(
                    module(appContext)
                        .callAttr("get_runtime_state")
                        .toString(),
                )
                publish(
                    snapshotFromRuntimeState(
                        RuntimeSnapshot(
                            phase = RuntimePhase.READY,
                            message = "Кира:Ядро готово",
                            genomeRevision = result.optInt("genome_revision"),
                            genomeSha256 = result.optString("genome_sha256"),
                        ),
                        runtimeState,
                    ),
                )
            } catch (error: Throwable) {
                roomPersistence?.close()
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

    fun getGenomeInfo(context: Context): BridgeGenomeInfo {
        ensureReady()
        return BridgeJsonParser.genome(
            JSONObject(
                module(context.applicationContext)
                    .callAttr("get_genome_info")
                    .toString(),
            ),
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
        val result = JSONObject(raw.toString())
        publish(
            currentSnapshot.copy(
                activeSessionId = result.optString("session_id").takeIf { it.isNotBlank() },
                turn = 0,
                pulse = null,
            ),
        )
        return result
    }

    fun createSessionTyped(
        context: Context,
        provider: String,
        model: String,
        identityId: String? = null,
    ): BridgeSession =
        BridgeJsonParser.session(
            createSession(context, provider, model, identityId),
        )

    fun listSessions(context: Context): List<BridgeSession> {
        ensureReady()
        val array = JSONArray(
            module(context.applicationContext)
                .callAttr("list_sessions")
                .toString(),
        )
        return buildList(array.length()) {
            for (index in 0 until array.length()) {
                add(BridgeJsonParser.session(array.getJSONObject(index)))
            }
        }
    }

    fun resumeSession(
        context: Context,
        sessionId: String? = null,
    ): BridgeResumeResult {
        ensureReady()
        val pyModule = module(context.applicationContext)
        val result = if (sessionId == null) {
            JSONObject(pyModule.callAttr("resume_session").toString())
        } else {
            JSONObject(pyModule.callAttr("resume_session", sessionId).toString())
        }
        val runtimeState = BridgeJsonParser.runtimeState(
            result.getJSONObject("runtime_state"),
        )
        publish(
            snapshotFromRuntimeState(
                currentSnapshot.copy(
                    phase = RuntimePhase.READY,
                    message = "Кира:Ядро готово",
                ),
                result.getJSONObject("runtime_state"),
            ),
        )
        val session = result.optJSONObject("session")?.let(BridgeJsonParser::session)
        return BridgeResumeResult(session = session, runtimeState = runtimeState)
    }

    fun getRuntimeState(context: Context): JSONObject {
        ensureReady()
        val state = JSONObject(
            module(context.applicationContext)
                .callAttr("get_runtime_state")
                .toString(),
        )
        syncSnapshot(state)
        return state
    }

    fun getRuntimeStateTyped(context: Context): BridgeRuntimeState =
        BridgeJsonParser.runtimeState(getRuntimeState(context))

    fun getConversation(
        context: Context,
        sessionId: String,
        limit: Int = 20,
    ): List<BridgeConversationMessage> {
        require(limit >= 0) { "Лимит разговора не может быть отрицательным." }
        ensureReady()
        val array = JSONArray(
            module(context.applicationContext)
                .callAttr("get_conversation", sessionId, limit)
                .toString(),
        )
        return buildList(array.length()) {
            for (index in 0 until array.length()) {
                add(BridgeJsonParser.conversation(array.getJSONObject(index)))
            }
        }
    }

    fun getMemory(context: Context): List<BridgeMemoryRecord> {
        ensureReady()
        return parseMemoryArray(
            JSONArray(
                module(context.applicationContext)
                    .callAttr("get_memory")
                    .toString(),
            ),
        )
    }

    fun getMemoryCandidates(context: Context): List<BridgeMemoryRecord> {
        ensureReady()
        return parseMemoryArray(
            JSONArray(
                module(context.applicationContext)
                    .callAttr("get_memory_candidates")
                    .toString(),
            ),
        )
    }

    fun runTestTurn(context: Context, sessionId: String, task: String): JSONObject {
        ensureReady()
        val result = JSONObject(
            module(context.applicationContext)
                .callAttr("send_test_turn", sessionId, task)
                .toString(),
        )
        syncSnapshot(result.optJSONObject("runtime_state"))
        return result
    }

    fun sendTestTurnTyped(
        context: Context,
        sessionId: String,
        task: String,
    ): BridgeTestTurnResult {
        val result = runTestTurn(context, sessionId, task)
        val response = result.getJSONObject("response")
        val runtimeState = BridgeJsonParser.runtimeState(
            result.getJSONObject("runtime_state"),
        )
        return BridgeTestTurnResult(
            text = response.optString("text"),
            provider = response.optString("provider"),
            model = response.optString("model"),
            pulse = BridgeJsonParser.pulse(response.optJSONObject("raw_metadata")?.optJSONObject("pulse")),
            runtimeState = runtimeState,
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

    fun checkHealth(context: Context): BridgeHealth {
        ensureReady()
        return BridgeJsonParser.health(
            JSONObject(
                module(context.applicationContext)
                    .callAttr("check_health")
                    .toString(),
            ),
        )
    }

    fun health(context: Context): String {
        if (currentSnapshot.phase != RuntimePhase.READY) {
            return currentSnapshot.message
        }
        return module(context.applicationContext).callAttr("health").toString()
    }

    fun shutdown(context: Context) {
        shutdownOnExecutor(context.applicationContext)
    }

    fun shutdownAsync(context: Context) {
        if (currentSnapshot.phase == RuntimePhase.STOPPED ||
            currentSnapshot.phase == RuntimePhase.STOPPING
        ) {
            return
        }

        publish(
            currentSnapshot.copy(
                phase = RuntimePhase.STOPPING,
                message = "Остановка Кира:Ядра…",
                error = null,
            ),
        )
        val appContext = context.applicationContext
        executor.execute {
            shutdownOnExecutor(appContext)
        }
    }

    private fun shutdownOnExecutor(context: Context) {
        if (currentSnapshot.phase == RuntimePhase.STOPPED) {
            return
        }
        runCatching {
            module(context).callAttr("shutdown")
        }.onSuccess {
            publish(RuntimeSnapshot())
        }.onFailure { error ->
            publish(
                RuntimeSnapshot(
                    phase = RuntimePhase.FAILED,
                    message = "Ошибка остановки Кира:Ядра",
                    error = error.message ?: error::class.java.simpleName,
                ),
            )
        }
    }

    private fun parseMemoryArray(array: JSONArray): List<BridgeMemoryRecord> =
        buildList(array.length()) {
            for (index in 0 until array.length()) {
                add(BridgeJsonParser.memory(array.getJSONObject(index)))
            }
        }

    private fun ensureReady() {
        check(currentSnapshot.phase == RuntimePhase.READY) {
            "Кира:Ядро ещё не готово."
        }
    }

    private fun snapshotFromRuntimeState(
        base: RuntimeSnapshot,
        state: JSONObject?,
    ): RuntimeSnapshot {
        if (state == null) return base
        return base.copy(
            activeSessionId = state.optString("active_session_id")
                .takeIf { it.isNotBlank() },
            turn = state.optInt("turn", 0),
            pulse = state.optJSONObject("pulse")
                ?.optInt("value")
                ?.takeIf { it != 0 },
        )
    }

    private fun syncSnapshot(state: JSONObject?) {
        if (state == null) return
        currentSnapshot = snapshotFromRuntimeState(currentSnapshot, state)
        listeners.forEach { listener ->
            runCatching { listener(currentSnapshot) }
        }
    }

    private fun publish(next: RuntimeSnapshot) {
        currentSnapshot = next
        listeners.forEach { listener ->
            runCatching { listener(next) }
        }
    }
    /** A2 physical persistence gateway exposed for diagnostics and integration boundaries. */
    fun openRoomPersistence(context: Context): ru.kiracore.ai.storage.room.AndroidRoomPersistenceGateway =
        ru.kiracore.ai.storage.room.AndroidRoomPersistenceGateway(context.applicationContext)

}
