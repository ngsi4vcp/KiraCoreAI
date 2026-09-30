package ru.kiracore.ai.runtime

enum class RuntimePhase {
    STOPPED,
    INITIALIZING,
    READY,
    FAILED,
    STOPPING,
}

data class RuntimeSnapshot(
    val phase: RuntimePhase = RuntimePhase.STOPPED,
    val message: String = "Кира:Ядро остановлено",
    val error: String? = null,
    val genomeRevision: Int? = null,
    val genomeSha256: String? = null,
    val activeSessionId: String? = null,
    val turn: Int = 0,
    val pulse: Int? = null,
)
