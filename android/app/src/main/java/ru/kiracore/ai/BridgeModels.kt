package ru.kiracore.ai

import org.json.JSONArray
import org.json.JSONObject

data class BridgePulse(
    val series: Int,
    val revision: Int,
    val turn: Int,
    val value: Int,
    val key: String,
)

data class BridgeGenomeInfo(
    val revision: Int,
    val series: Int,
    val sha256: String,
    val sectionCount: Int,
)

data class BridgeSession(
    val sessionId: String,
    val createdAt: String,
    val updatedAt: String,
    val provider: String,
    val model: String,
    val title: String,
)

data class BridgeMemoryRecord(
    val id: String,
    val type: String,
    val content: String,
    val timestamp: String,
    val source: String,
    val confidence: Double?,
    val importance: Double,
    val provenance: String,
    val entities: List<String>,
    val validFrom: String?,
    val validTo: String?,
    val status: String,
    val ownerIdentityId: String?,
    val privacyScope: String,
)

data class BridgeConversationMessage(
    val id: String,
    val sessionId: String,
    val turn: Int,
    val role: String,
    val content: String,
    val timestamp: String,
    val pulse: BridgePulse?,
)

data class BridgeRuntimeState(
    val schemaVersion: Int,
    val runtimeStatus: String?,
    val activeSessionId: String?,
    val identityId: String?,
    val turn: Int,
    val pulse: BridgePulse?,
    val activeProvider: String?,
    val activeModel: String?,
    val authorizedAlek: Boolean,
    val lastError: String?,
    val rawState: JSONObject,
)

data class BridgeHealth(
    val status: String,
    val runtimeStatus: String?,
    val activeSessionId: String?,
    val turn: Int,
    val pulse: BridgePulse?,
)

data class BridgeResumeResult(
    val session: BridgeSession?,
    val runtimeState: BridgeRuntimeState,
)

data class BridgeTestTurnResult(
    val text: String,
    val provider: String,
    val model: String,
    val pulse: BridgePulse?,
    val runtimeState: BridgeRuntimeState,
)

internal object BridgeJsonParser {
    fun pulse(value: JSONObject?): BridgePulse? {
        if (value == null) return null
        return BridgePulse(
            series = value.optInt("series"),
            revision = value.optInt("revision"),
            turn = value.optInt("turn"),
            value = value.optInt("value"),
            key = value.optString("key"),
        )
    }

    fun genome(value: JSONObject): BridgeGenomeInfo =
        BridgeGenomeInfo(
            revision = value.optInt("revision"),
            series = value.optInt("series"),
            sha256 = value.optString("sha256"),
            sectionCount = value.optInt("section_count"),
        )

    fun session(value: JSONObject): BridgeSession =
        BridgeSession(
            sessionId = value.optString("session_id"),
            createdAt = value.optString("created_at"),
            updatedAt = value.optString("updated_at"),
            provider = value.optString("provider"),
            model = value.optString("model"),
            title = value.optString("title"),
        )

    fun runtimeState(value: JSONObject): BridgeRuntimeState =
        BridgeRuntimeState(
            schemaVersion = value.optInt("schema_version"),
            runtimeStatus = value.optString("runtime_status").takeIf { it.isNotBlank() },
            activeSessionId = value.optString("active_session_id")
                .takeIf { it.isNotBlank() },
            identityId = value.optString("identity_id").takeIf { it.isNotBlank() },
            turn = value.optInt("turn"),
            pulse = pulse(value.optJSONObject("pulse")),
            activeProvider = value.optString("active_provider")
                .takeIf { it.isNotBlank() },
            activeModel = value.optString("active_model")
                .takeIf { it.isNotBlank() },
            authorizedAlek = value.optBoolean("authorized_alek"),
            lastError = value.optString("last_error").takeIf { it.isNotBlank() },
            rawState = value.optJSONObject("state") ?: JSONObject(),
        )

    fun health(value: JSONObject): BridgeHealth =
        BridgeHealth(
            status = value.optString("status"),
            runtimeStatus = value.optString("runtime_status")
                .takeIf { it.isNotBlank() },
            activeSessionId = value.optString("active_session_id")
                .takeIf { it.isNotBlank() },
            turn = value.optInt("turn"),
            pulse = pulse(value.optJSONObject("pulse")),
        )

    fun memory(value: JSONObject): BridgeMemoryRecord =
        BridgeMemoryRecord(
            id = value.optString("id"),
            type = value.optString("type"),
            content = value.optString("content"),
            timestamp = value.optString("timestamp"),
            source = value.optString("source"),
            confidence = if (value.isNull("confidence")) {
                null
            } else {
                value.optDouble("confidence").takeIf { !it.isNaN() }
            },
            importance = value.optDouble("importance", 0.5),
            provenance = value.optString("provenance"),
            entities = value.optJSONArray("entities").toStringList(),
            validFrom = value.optString("valid_from").takeIf { it.isNotBlank() },
            validTo = value.optString("valid_to").takeIf { it.isNotBlank() },
            status = value.optString("status"),
            ownerIdentityId = value.optString("owner_identity_id")
                .takeIf { it.isNotBlank() },
            privacyScope = value.optString("privacy_scope"),
        )

    fun conversation(value: JSONObject): BridgeConversationMessage =
        BridgeConversationMessage(
            id = value.optString("id"),
            sessionId = value.optString("session_id"),
            turn = value.optInt("turn"),
            role = value.optString("role"),
            content = value.optString("content"),
            timestamp = value.optString("timestamp"),
            pulse = pulse(value.optJSONObject("pulse")),
        )

    private fun JSONArray?.toStringList(): List<String> {
        if (this == null) return emptyList()
        return buildList(length()) {
            for (index in 0 until length()) {
                add(optString(index))
            }
        }
    }
}
