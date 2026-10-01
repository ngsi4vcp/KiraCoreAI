package ru.kiracore.ai.debug

import android.content.ContentResolver
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Process
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import ru.kiracore.ai.BuildConfig
import ru.kiracore.ai.KiraRuntimeBridge
import ru.kiracore.ai.security.AndroidCryptoProvider
import ru.kiracore.ai.security.AndroidSecureStore
import ru.kiracore.ai.storage.AndroidStorageProbe
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

data class EvidenceCheck(
    val name: String,
    val status: String,
    val durationMs: Long,
    val details: String,
)

data class DeviceEvidenceUiState(
    val runId: String? = null,
    val phase: String = "Ожидание",
    val running: Boolean = false,
    val recoveryPending: Boolean = false,
    val overall: String = "НЕ ЗАПУЩЕНО",
    val checks: List<EvidenceCheck> = emptyList(),
)

private data class PendingRecovery(
    val runId: String,
    val sessionId: String,
    val turn: Int,
    val pulse: Int?,
)

class DeviceEvidenceRunner(
    private val context: Context,
) {
    private val scope = CoroutineScope(Job() + Dispatchers.IO)
    private val root = File(context.filesDir, "device-evidence")
    private val checkpoint = File(root, "pending-recovery.json")
    private val expectedGenomeRevision = 22
    private val expectedGenomeSha256 =
        "dde7ce4b640f9dbcbeed6201559fb118849058e25ceccb9befa663e8ce6b726e"

    private val _state = MutableStateFlow(DeviceEvidenceUiState())
    val state: StateFlow<DeviceEvidenceUiState> = _state

    init {
        root.mkdirs()
        _state.value = _state.value.copy(recoveryPending = checkpoint.isFile)
        restoreLatestEvidenceState()
    }

    fun close() {
        scope.cancel()
    }

    fun observeLifecycle(event: String) {
        appendEvent(
            runDirForCurrent(),
            "lifecycle.$event",
            "OBSERVED",
            JSONObject().put("activity", "DeviceEvidenceActivity"),
        )
    }

    fun startFullSmoke() {
        if (_state.value.running) return
        val runId = timestamp()
        val runDir = File(root, runId).apply { mkdirs() }
        _state.value = DeviceEvidenceUiState(
            runId = runId,
            phase = "A0.D1: проверка",
            running = true,
            overall = "ВЫПОЛНЯЕТСЯ",
        )
        scope.launch {
            try {
                runCheck(runDir, "Окружение") { environmentCheck() }
                waitForRuntime(runDir)
                runCheck(runDir, "GENOME") { genomeCheck() }
                runCheck(runDir, "Диагностика") { diagnosticsCheck() }
                val sessionId = runCheck(runDir, "Тестовая сессия") { sessionCheck() }
                runCheck(runDir, "Тестовый ход") { deterministicTurnCheck(sessionId) }
                runCheck(runDir, "ПУЛЬС и состояние") { pulseStateCheck() }
                runCheck(runDir, "Android Keystore") { keystoreCheck() }
                runCheck(runDir, "Хранилище") { storageCheck() }
                writeManifest(runDir, "COMPLETED")
                setOverall("A0.D1: базовая проверка завершена")
            } catch (error: CancellationException) {
                throw error
            } catch (error: Throwable) {
                appendEvent(
                    runDir,
                    "smoke.failed",
                    "FAIL",
                    JSONObject()
                        .put("exception", error::class.java.name)
                        .put("message", error.message ?: error::class.java.simpleName),
                )
                writeManifest(runDir, "FAILED")
                setOverall("ОШИБКА: ${error::class.java.simpleName}")
            }
        }
    }

    fun startA1ParitySmoke() {
        if (_state.value.running) return
        val runId = timestamp()
        val runDir = File(root, runId).apply { mkdirs() }
        _state.value = DeviceEvidenceUiState(
            runId = runId,
            phase = "A1.0/A1.2: проверка соответствия",
            running = true,
            overall = "ВЫПОЛНЯЕТСЯ",
        )
        scope.launch {
            try {
                runCheck(runDir, "A1: состояние рантайма") {
                    waitForRuntime(runDir)
                    val health = KiraRuntimeBridge.checkHealth(context)
                    require(health.status == "READY") {
                        "Structured health не READY: ${health.status}"
                    }
                    "status=${health.status}, turn=${health.turn}"
                }
                runCheck(runDir, "A1: сведения о GENOME") {
                    val genome = KiraRuntimeBridge.getGenomeInfo(context)
                    require(genome.revision == expectedGenomeRevision)
                    require(genome.series == 1000)
                    require(genome.sha256 == expectedGenomeSha256)
                    "revision=${genome.revision}, series=${genome.series}"
                }
                val sessionId = runCheck(runDir, "A1: создание сессии") {
                    KiraRuntimeBridge.createSessionTyped(
                        context,
                        provider = "a0-test",
                        model = "embedded/a0-test",
                    ).also {
                        require(it.sessionId.isNotBlank()) { "Session ID не получен." }
                    }.sessionId
                }
                runCheck(runDir, "A1: список сессий") {
                    val sessions = KiraRuntimeBridge.listSessions(context)
                    require(sessions.any { it.sessionId == sessionId }) {
                        "Созданная сессия отсутствует в list_sessions."
                    }
                    "count=${sessions.size}"
                }
                runCheck(runDir, "A1: восстановление сессии") {
                    val resumed = KiraRuntimeBridge.resumeSession(context, sessionId)
                    require(resumed.session?.sessionId == sessionId) {
                        "resume_session вернул другую сессию."
                    }
                    require(resumed.runtimeState.activeSessionId == sessionId)
                    require(resumed.runtimeState.turn == 0)
                    require(resumed.runtimeState.pulse == null)
                    "session=${resumed.runtimeState.activeSessionId}, turn=0, pulse=null"
                }
                runCheck(runDir, "A1: детерминированный ход") {
                    val turn = KiraRuntimeBridge.sendTestTurnTyped(
                        context,
                        sessionId,
                        "~1 Диагностический A1 parity turn.",
                    )
                    require(turn.runtimeState.activeSessionId == sessionId)
                    require(turn.runtimeState.turn == 1)
                    require(turn.runtimeState.authorizedAlek) {
                        "Семантика ~1 не установила authorized_alek."
                    }
                    require(turn.pulse?.value == 1024)
                    "turn=${turn.runtimeState.turn}, pulse=${turn.pulse?.value}"
                }
                runCheck(runDir, "A1: разговор") {
                    val messages = KiraRuntimeBridge.getConversation(context, sessionId, 20)
                    require(messages.size >= 2) {
                        "Ожидались user+assistant сообщения."
                    }
                    val tail = messages.takeLast(2)
                    require(tail[0].role == "user")
                    require(!tail[0].content.contains("~1"))
                    require(tail[0].content == "Диагностический A1 parity turn.")
                    require(tail[1].role == "assistant")
                    require(tail[1].pulse?.value == 1024)
                    "messages=${messages.size}, last_turn=${tail[1].turn}"
                }
                runCheck(runDir, "A1: разделение памяти") {
                    val approved = KiraRuntimeBridge.getMemory(context)
                    val candidates = KiraRuntimeBridge.getMemoryCandidates(context)
                    require(approved.isEmpty()) {
                        "В чистом parity smoke появилась approved memory."
                    }
                    require(candidates.isEmpty()) {
                        "В чистом parity smoke появились memory candidates."
                    }
                    "approved=0, candidates=0"
                }
                runCheck(runDir, "A1: структурированное состояние после хода") {
                    val health = KiraRuntimeBridge.checkHealth(context)
                    require(health.status == "READY")
                    require(health.activeSessionId == sessionId)
                    require(health.turn == 1)
                    require(health.pulse?.value == 1024)
                    require(health.operation?.phase == "COMPLETED") {
                        "Operation phase не COMPLETED: ${health.operation?.phase}"
                    }
                    require(health.operation?.recoveryState == "COMPLETED") {
                        "Recovery state не COMPLETED: ${health.operation?.recoveryState}"
                    }
                    "session=${health.activeSessionId}, turn=${health.turn}, pulse=${health.pulse?.value}, operation=${health.operation?.phase}"
                }
                writeManifest(runDir, "COMPLETED", "android-a1-device")
                setOverall("A1.0/A1.2: проверка соответствия завершена")
            } catch (error: CancellationException) {
                throw error
            } catch (error: Throwable) {
                appendEvent(
                    runDir,
                    "a1.smoke.failed",
                    "FAIL",
                    JSONObject()
                        .put("exception", error::class.java.name)
                        .put("message", error.message ?: error::class.java.simpleName),
                )
                writeManifest(runDir, "FAILED", "android-a1-device")
                setOverall("A1: блокирующая ошибка — ${error::class.java.simpleName}")
            }
        }
    }

    fun startA2PersistenceSmoke() {
        if (_state.value.running) return
        val runId = timestamp()
        val runDir = File(root, runId).apply { mkdirs() }
        _state.value = DeviceEvidenceUiState(
            runId = runId,
            phase = "A2.1: физическая персистентность",
            running = true,
            overall = "ВЫПОЛНЯЕТСЯ",
        )
        scope.launch {
            try {
                waitForRuntime(runDir)
                runCheck(runDir, "A2.1: backend identity") {
                    val diagnostics = KiraRuntimeBridge.diagnostics(context)
                    require(diagnostics.optString("persistence_backend") == "android-room") {
                        "Ожидался android-room, получено: " +
                            diagnostics.optString("persistence_backend")
                    }
                    "backend=${diagnostics.optString("persistence_backend")}"
                }
                val sessionId = runCheck(runDir, "A2.1: запись session/conversation") {
                    val session = KiraRuntimeBridge.createSession(
                        context = context,
                        provider = "a0-test",
                        model = "embedded/a0-test",
                    )
                    val id = session.optString("session_id")
                    require(id.isNotBlank()) { "Session ID не получен." }
                    val turn = KiraRuntimeBridge.runTestTurn(
                        context = context,
                        sessionId = id,
                        task = "Диагностический A2.1 persistence turn.",
                    )
                    require(turn.optJSONObject("runtime_state")?.optInt("turn") == 1) {
                        "После тестового хода turn не равен 1."
                    }
                    require(
                        turn.optJSONObject("response")?.optString("text").orEmpty().isNotBlank()
                    )
                    id
                }

                runCheck(runDir, "A2.1: перед restart") {
                    val state = KiraRuntimeBridge.getRuntimeState(context)
                    require(state.optString("active_session_id") == sessionId)
                    require(state.optInt("turn") == 1)
                    require(
                        state.optJSONObject("operation")?.optString("phase") == "COMPLETED"
                    )
                    val messages = KiraRuntimeBridge.getConversation(context, sessionId, 20)
                    require(messages.size >= 2) {
                        "До restart не найдены user+assistant сообщения."
                    }
                    "messages=${messages.size}, turn=${state.optInt("turn")}"
                }

                runCheck(runDir, "A2.1: закрытие runtime и новый backend") {
                    KiraRuntimeBridge.shutdown(context)
                    require(KiraRuntimeBridge.snapshot().phase.name == "STOPPED")
                    "runtime остановлен"
                }

                waitForRuntime(runDir)

                runCheck(runDir, "A2.1: read-back session/state/operation") {
                    val resumed = KiraRuntimeBridge.resumeSession(context, sessionId)
                    require(resumed.session?.sessionId == sessionId) {
                        "Session после restart не восстановлена."
                    }
                    require(resumed.runtimeState.turn == 1)
                    require(resumed.runtimeState.activeSessionId == sessionId)
                    val health = KiraRuntimeBridge.checkHealth(context)
                    require(health.operation?.phase == "COMPLETED") {
                        "Operation после restart не COMPLETED: ${health.operation?.phase}"
                    }
                    require(health.operation?.recoveryState == "COMPLETED")
                    "session=$sessionId, turn=1, operation=COMPLETED"
                }

                runCheck(runDir, "A2.1: read-back conversation") {
                    val messages = KiraRuntimeBridge.getConversation(context, sessionId, 20)
                    require(messages.size >= 2)
                    require(messages[0].role == "user")
                    require(messages[0].content == "Диагностический A2.1 persistence turn.")
                    require(messages[1].role == "assistant")
                    require(messages[1].pulse?.value == 1024)
                    "messages=${messages.size}, pulse=${messages[1].pulse?.value}"
                }

                runCheck(runDir, "A2.1: backend identity после restart") {
                    val diagnostics = KiraRuntimeBridge.diagnostics(context)
                    require(diagnostics.optString("persistence_backend") == "android-room")
                    "backend=${diagnostics.optString("persistence_backend")}"
                }

                runCheck(runDir, "A2.1: canonical JSON guard") {
                    val dataRoot = File(context.filesDir, "DATA")
                    val jsonFiles = dataRoot.walkTopDown()
                        .filter { it.isFile && (it.extension == "json" || it.extension == "jsonl") }
                        .toList()
                    require(jsonFiles.isEmpty()) {
                        "Обнаружен canonical JSON/JSONL в Room mode: " +
                            jsonFiles.joinToString(",") { it.relativeTo(dataRoot).path }
                    }
                    "DATA без JSON/JSONL"
                }

                runCheck(runDir, "A2.1: payload encryption at rest") {
                    val markers = listOf(
                        "Диагностический A2.1 persistence turn.",
                        "Тестовый ход A0 успешно выполнен.",
                    )
                    val database = context.getDatabasePath("kira-core.db")
                    val databaseCandidates = listOf(
                        database,
                        File(database.parentFile, "kira-core.db-wal"),
                        File(database.parentFile, "kira-core.db-shm"),
                    )
                    val readable = databaseCandidates.filter { it.isFile }
                    require(readable.isNotEmpty()) { "Room database files не найдены." }
                    val plaintext = readable.any { file ->
                        val data = file.readBytes()
                        markers.any { marker ->
                            containsBytes(data, marker.toByteArray(Charsets.UTF_8))
                        }
                    }
                    require(!plaintext) {
                        "Известный conversation payload обнаружен в Room files в plaintext."
                    }
                    "известный payload не обнаружен в DB/WAL/SHM"
                }

                appendEvent(
                    runDir,
                    "a2.1.device.persistence.completed",
                    "PASS",
                    JSONObject().put("session_id", sessionId).put("backend", "android-room"),
                )
                writeManifest(runDir, "A2_1_PERSISTENCE_OK", "android-a2.1-device")
                setOverall("A2.1: физическая персистентность подтверждена")
            } catch (error: CancellationException) {
                throw error
            } catch (error: Throwable) {
                appendEvent(
                    runDir,
                    "a2.1.device.persistence.failed",
                    "FAIL",
                    JSONObject()
                        .put("exception", error::class.java.name)
                        .put("message", error.message ?: error::class.java.simpleName),
                )
                writeManifest(runDir, "FAILED", "android-a2.1-device")
                setOverall("A2.1: блокирующая ошибка — ${error::class.java.simpleName}")
            }
        }
    }
    fun prepareAndRestart() {
        if (_state.value.running) return
        scope.launch {
            try {
                val snapshot = KiraRuntimeBridge.snapshot()
                val sessionId = snapshot.activeSessionId
                    ?: error("Нет активной тестовой сессии для recovery-check.")
                val runId = _state.value.runId ?: error("Нет текущего evidence run.")
                val runDir = File(root, runId)
                checkpoint.writeText(
                    JSONObject()
                        .put("run_id", runId)
                        .put("session_id", sessionId)
                        .put("turn", snapshot.turn)
                        .put("pulse", snapshot.pulse ?: JSONObject.NULL)
                        .put("genome_revision", snapshot.genomeRevision ?: JSONObject.NULL)
                        .put("genome_sha256", snapshot.genomeSha256 ?: JSONObject.NULL)
                        .toString(2),
                    Charsets.UTF_8,
                )
                appendEvent(
                    runDir,
                    "recovery.checkpoint_created",
                    "PASS",
                    JSONObject()
                        .put("session_id", sessionId)
                        .put("turn", snapshot.turn),
                )
                withContext(Dispatchers.Main) {
                    _state.value = _state.value.copy(
                        running = false,
                        phase = "Перезапуск процесса…",
                        recoveryPending = true,
                    )
                }
                delay(400)
                Process.killProcess(Process.myPid())
            } catch (error: CancellationException) {
                throw error
            } catch (error: Throwable) {
                setOverall("Recovery подготовка: ${error::class.java.simpleName}")
            }
        }
    }

    fun recoverPending() {
        if (!checkpoint.isFile || _state.value.running) return
        val pending = runCatching {
            val json = JSONObject(checkpoint.readText(Charsets.UTF_8))
            PendingRecovery(
                runId = json.getString("run_id"),
                sessionId = json.getString("session_id"),
                turn = json.getInt("turn"),
                pulse = if (json.isNull("pulse")) null else json.getInt("pulse"),
            )
        }.getOrElse {
            checkpoint.delete()
            setOverall("Recovery checkpoint повреждён")
            return
        }

        val runDir = File(root, pending.runId)
        _state.value = DeviceEvidenceUiState(
            runId = pending.runId,
            phase = "Recovery после process death",
            running = true,
            recoveryPending = true,
            overall = "ВЫПОЛНЯЕТСЯ",
        )
        scope.launch {
            try {
                waitForRuntime(runDir)
                runCheck(runDir, "Восстановление: GENOME") { genomeCheck() }
                runCheck(runDir, "Восстановление: сессия/состояние") {
                    val state = KiraRuntimeBridge.getRuntimeState(context)
                    val actualSession = state.optString("active_session_id")
                        .takeIf { it.isNotBlank() }
                    val actualTurn = state.optInt("turn", 0)
                    require(actualSession == pending.sessionId) {
                        "active_session_id после restart не совпал."
                    }
                    require(actualTurn == pending.turn) {
                        "turn после restart не совпал."
                    }
                    "session=${actualSession}, turn=${actualTurn}"
                }
                runCheck(runDir, "Recovery: ПУЛЬС") {
                    val state = KiraRuntimeBridge.getRuntimeState(context)
                    val pulse = state.optJSONObject("pulse")
                        ?.optInt("value")
                        ?.takeIf { it != 0 }
                    require(pulse == pending.pulse) {
                        "Pulse после restart не совпал."
                    }
                    "pulse=${pulse}"
                }
                appendEvent(
                    runDir,
                    "recovery.completed",
                    "PASS",
                    JSONObject().put("run_id", pending.runId),
                )
                checkpoint.delete()
                completeRecoveryEvidence(runDir)
                setOverall(recoveryOverall(runDir))
            } catch (error: CancellationException) {
                throw error
            } catch (error: Throwable) {
                appendEvent(
                    runDir,
                    "recovery.failed",
                    "FAIL",
                    JSONObject().put("exception", error::class.java.name),
                )
                setOverall("Восстановление: блокирующая ошибка — ${error::class.java.simpleName}")
            }
        }
    }

    fun exportEvidence(uri: Uri, resolver: ContentResolver) {
        val runId = _state.value.runId ?: return
        val runDir = File(root, runId)
        if (!runDir.isDirectory) return
        scope.launch {
            runCatching {
                resolver.openOutputStream(uri)?.use { output ->
                    ZipOutputStream(output).use { zip ->
                        addDirectory(zip, runDir, runDir)
                    }
                } ?: error("Не удалось открыть файл экспорта.")
            }.onSuccess {
                setOverall("Evidence bundle экспортирован")
            }.onFailure {
                setOverall("Экспорт не выполнен: ${it::class.java.simpleName}")
            }
        }
    }

    private suspend fun waitForRuntime(runDir: File) {
        var reinitializeAttempted = false
        repeat(480) { iteration ->
            val snapshot = KiraRuntimeBridge.snapshot()
            when (snapshot.phase.name) {
                "READY" -> return
                "INITIALIZING" -> {
                    updatePhase("Инициализация runtime: ${snapshot.message}")
                }
                "STOPPED" -> {
                    if (!reinitializeAttempted) {
                        reinitializeAttempted = true
                        appendEvent(
                            runDir,
                            "runtime.reinitialize_requested",
                            "PASS",
                            JSONObject().put("reason", "STOPPED"),
                        )
                        KiraRuntimeBridge.initializeAsync(context)
                    }
                    updatePhase("Runtime остановлен — повторная инициализация…")
                }
                "FAILED" -> {
                    if (!reinitializeAttempted) {
                        reinitializeAttempted = true
                        appendEvent(
                            runDir,
                            "runtime.reinitialize_requested",
                            "PASS",
                            JSONObject().put("reason", "FAILED"),
                        )
                        KiraRuntimeBridge.initializeAsync(context)
                        updatePhase("Runtime завершился с ошибкой — повторная инициализация…")
                    } else {
                        appendEvent(
                            runDir,
                            "runtime.failed",
                            "FAIL",
                            JSONObject().put("error", snapshot.error ?: snapshot.message),
                        )
                        error(
                            "Runtime завершился с FAILED: " +
                                (snapshot.error ?: snapshot.message),
                        )
                    }
                }
                "STOPPING" -> {
                    updatePhase("Runtime останавливается…")
                }
            }
            if (iteration % 20 == 0) {
                updatePhase(KiraRuntimeBridge.snapshot().message)
            }
            delay(250)
        }
        val snapshot = KiraRuntimeBridge.snapshot()
        appendEvent(
            runDir,
            "runtime.wait_timeout",
            "FAIL",
            JSONObject()
                .put("phase", snapshot.phase.name)
                .put("error", snapshot.error ?: JSONObject.NULL),
        )
        error(
            "Runtime не достиг READY за 120s: " +
                "phase=" + snapshot.phase + ", error=" + (snapshot.error ?: "нет"),
        )
    }

    private suspend fun updatePhase(message: String) {
        withContext(Dispatchers.Main) {
            _state.value = _state.value.copy(phase = message)
        }
    }
    private fun restoreLatestEvidenceState() {
        val latestRun = root.listFiles()
            ?.asSequence()
            ?.filter { it.isDirectory }
            ?.sortedByDescending { it.name }
            ?.firstOrNull { File(it, "manifest.json").isFile }
            ?: return
        runCatching {
            val manifest = JSONObject(
                File(latestRun, "manifest.json").readText(Charsets.UTF_8),
            )
            val status = manifest.optString("status", "UNKNOWN")
            val overall = when (status) {
                "RECOVERY_OK" -> "Последняя проверка: RECOVERY_OK"
                "COMPLETED" -> "Последняя проверка: завершена"
                "FAILED" -> "Последняя проверка: завершилась с ошибкой"
                "A2_1_PERSISTENCE_OK" -> "Последняя проверка: A2.1 persistence подтверждена"
                else -> "Последняя проверка: $status"
            }
            _state.value = DeviceEvidenceUiState(
                runId = manifest.optString("run_id").takeIf { it.isNotBlank() }
                    ?: latestRun.name,
                phase = "Готово",
                running = false,
                recoveryPending = checkpoint.isFile,
                overall = overall,
            )
        }
    }
    private fun environmentCheck(): String {
        val abis = Build.SUPPORTED_ABIS.joinToString(",")
        require("arm64-v8a" in Build.SUPPORTED_ABIS) {
            "Устройство не сообщает arm64-v8a."
        }
        return "Android API ${Build.VERSION.SDK_INT}, ${Build.MANUFACTURER} ${Build.MODEL}, ABI=${abis}"
    }

    private fun genomeCheck(): String {
        val result = KiraRuntimeBridge.loadGenome(context)
        val revision = result.optInt("genome_revision")
        val sha = result.optString("genome_sha256")
        require(revision == expectedGenomeRevision) {
            "Ожидалась GENOME revision ${expectedGenomeRevision}, получена ${revision}."
        }
        require(sha == expectedGenomeSha256) {
            "GENOME SHA-256 не совпал."
        }
        return "ревизия=${revision}, SHA-256=${sha}"
    }

    private fun diagnosticsCheck(): String {
        val diagnostics = KiraRuntimeBridge.diagnostics(context)
        require(diagnostics.optString("application_id") == BuildConfig.APPLICATION_ID)
        require(diagnostics.optBoolean("storage_writable"))
        require(diagnostics.optBoolean("secure_store_available"))
        return "ядро=${diagnostics.optString("core_version")}, Python=${diagnostics.optString("python_version")}"
    }

    private fun sessionCheck(): String {
        val result = KiraRuntimeBridge.createSession(
            context = context,
            provider = "a0-test",
            model = "embedded/a0-test",
        )
        val sessionId = result.optString("session_id")
        require(sessionId.isNotBlank()) { "Session ID не получен." }
        appendEvent(
            runDirForCurrent(),
            "session.created",
            "PASS",
            JSONObject().put("session_id", sessionId),
        )
        return sessionId
    }

    private fun deterministicTurnCheck(sessionId: String): String {
        val result = KiraRuntimeBridge.runTestTurn(
            context = context,
            sessionId = sessionId,
            task = "Диагностический тест A0.D1: выполнить детерминированный тестовый ход.",
        )
        val text = result.optJSONObject("response")?.optString("text").orEmpty()
        require(text.isNotBlank()) { "Пустой тестовый ответ." }
        return "ответ получен: да"
    }

    private fun pulseStateCheck(): String {
        val snapshot = KiraRuntimeBridge.snapshot()
        require(snapshot.activeSessionId != null) { "Нет active_session_id." }
        require(snapshot.turn > 0) { "turn не увеличился." }
        val expectedPulse = 1000 + expectedGenomeRevision +
            snapshot.turn + snapshot.turn * snapshot.turn
        require(snapshot.pulse == expectedPulse) {
            "Ожидался Pulse=${expectedPulse}, получен ${snapshot.pulse}."
        }
        return "сессия=${snapshot.activeSessionId}, ход=${snapshot.turn}, ПУЛЬС=${snapshot.pulse}"
    }

    private fun keystoreCheck(): String {
        val store = AndroidSecureStore(context)
        require(store.isAvailable()) { "Android Keystore недоступен." }
        val name = "device-evidence-${timestamp()}"
        val payload = AndroidCryptoProvider().randomBytes(32)
        store.put(name, payload)
        val restored = store.get(name)
        require(restored != null && restored.contentEquals(payload)) {
            "Keystore round-trip не совпал."
        }
        store.delete(name)
        require(store.get(name) == null) {
            "Keystore запись не удалена."
        }
        return "AES-GCM: проверка 32 байт — PASS"
    }

    private fun storageCheck(): String {
        val probe = AndroidStorageProbe(context)
        require(probe.isWritable()) { "DATA storage не доступен для записи." }
        val file = File(probe.rootPath(), ".device-evidence-read-probe")
        file.writeText("ok", Charsets.UTF_8)
        require(file.readText(Charsets.UTF_8) == "ok") {
            "Storage read probe не совпал."
        }
        file.delete()
        return "корень хранилища: чтение и запись доступны"
    }

    private suspend fun runCheck(
        runDir: File,
        name: String,
        block: suspend () -> String,
    ): String {
        val started = System.nanoTime()
        return try {
            withContext(Dispatchers.Main) {
                _state.value = _state.value.copy(phase = name)
            }
            val details = block()
            recordCheck(name, "PASS", elapsedMs(started), details)
            appendEvent(
                runDir,
                "check.completed",
                "PASS",
                JSONObject().put("check", name),
            )
            details
        } catch (error: CancellationException) {
            throw error
        } catch (error: Throwable) {
            recordCheck(name, "FAIL", elapsedMs(started), error::class.java.simpleName)
            appendEvent(
                runDir,
                "check.failed",
                "FAIL",
                JSONObject()
                    .put("check", name)
                    .put("exception", error::class.java.name),
            )
            throw error
        }
    }

    private fun recordCheck(
        name: String,
        status: String,
        durationMs: Long,
        details: String,
    ) {
        _state.value = _state.value.copy(
            checks = _state.value.checks +
                EvidenceCheck(name, status, durationMs, details),
        )
    }

    private fun setOverall(message: String) {
        _state.value = _state.value.copy(
            overall = message,
            running = false,
            phase = "Готово",
            recoveryPending = checkpoint.isFile,
        )
    }

    private fun completeRecoveryEvidence(runDir: File) {
        val manifestFile = File(runDir, "manifest.json")
        if (!manifestFile.isFile) {
            writeManifest(runDir, "RECOVERY_OK")
            return
        }

        runCatching {
            val manifest = JSONObject(
                manifestFile.readText(Charsets.UTF_8),
            )
            val evidenceType = manifest.optString("evidence_type")
            val status = manifest.optString("status")
            if (evidenceType == "android-a2.1-device" &&
                status == "A2_1_PERSISTENCE_OK"
            ) {
                manifest
                    .put("recovery_status", "RECOVERY_OK")
                    .put("recovery_checked_at", isoNow())
                manifestFile.writeText(
                    manifest.toString(2),
                    Charsets.UTF_8,
                )
                File(runDir, "README.txt").writeText(
                    "Диагностический evidence A2.1. Bundle не содержит секретов.\n",
                    Charsets.UTF_8,
                )
            } else {
                writeManifest(runDir, "RECOVERY_OK")
            }
        }.getOrElse {
            writeManifest(runDir, "RECOVERY_OK")
        }
    }

    private fun recoveryOverall(runDir: File): String {
        val manifestFile = File(runDir, "manifest.json")
        val manifest = runCatching {
            JSONObject(manifestFile.readText(Charsets.UTF_8))
        }.getOrNull()

        val isA21 = manifest?.let {
            it.optString("evidence_type") == "android-a2.1-device" &&
                it.optString("status") == "A2_1_PERSISTENCE_OK"
        } == true
        return if (isA21) {
            "A2.1: физическая персистентность и восстановление подтверждены"
        } else {
            "A0.D1 recovery после process death подтверждён"
        }
    }

    private fun writeManifest(
        runDir: File,
        status: String,
        evidenceType: String = "android-a0-device",
    ) {
        val manifest = JSONObject()
            .put("schema_version", 1)
            .put("evidence_type", evidenceType)
            .put("status", status)
            .put("run_id", runDir.name)
            .put("application_id", BuildConfig.APPLICATION_ID)
            .put("app_version", BuildConfig.VERSION_NAME)
            .put("genome_revision", expectedGenomeRevision)
            .put("genome_sha256", expectedGenomeSha256)
            .put("android_api", Build.VERSION.SDK_INT)
            .put("manufacturer", Build.MANUFACTURER)
            .put("model", Build.MODEL)
        File(runDir, "manifest.json").writeText(manifest.toString(2), Charsets.UTF_8)
        val readme = when (evidenceType) {
            "android-a2.1-device" ->
                "Диагностический evidence A2.1. Bundle не содержит секретов.\n"
            else ->
                "Диагностический evidence A0.D1. Bundle не содержит секретов.\n"
        }
        File(runDir, "README.txt").writeText(readme, Charsets.UTF_8)    }

    private fun containsBytes(haystack: ByteArray, needle: ByteArray): Boolean {
        if (needle.isEmpty()) return true
        if (needle.size > haystack.size) return false
        for (start in 0..haystack.size - needle.size) {
            var matches = true
            for (index in needle.indices) {
                if (haystack[start + index] != needle[index]) {
                    matches = false
                    break
                }
            }
            if (matches) return true
        }
        return false
    }

    private fun appendEvent(
        runDir: File,
        eventId: String,
        status: String,
        details: JSONObject = JSONObject(),
    ) {
        runDir.mkdirs()
        File(runDir, "events.jsonl").appendText(
            JSONObject()
                .put("timestamp", isoNow())
                .put("event_id", eventId)
                .put("status", status)
                .put("safe_details", details)
                .toString() + "\n",
            Charsets.UTF_8,
        )
    }

    private fun runDirForCurrent(): File =
        _state.value.runId?.let { File(root, it) } ?: root

    private fun addDirectory(
        zip: ZipOutputStream,
        base: File,
        current: File,
    ) {
        current.listFiles()?.sortedBy { it.name }?.forEach { file ->
            if (file.isDirectory) {
                addDirectory(zip, base, file)
            } else {
                val entryName = base.toPath().relativize(file.toPath()).toString()
                    .replace(File.separatorChar, '/')
                zip.putNextEntry(ZipEntry(entryName))
                file.inputStream().use { it.copyTo(zip) }
                zip.closeEntry()
            }
        }
    }

    private fun timestamp(): String =
        SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(Date())

    private fun isoNow(): String =
        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSXXX", Locale.US).format(Date())

    private fun elapsedMs(started: Long): Long =
        (System.nanoTime() - started).coerceAtLeast(0L) / 1_000_000L
}