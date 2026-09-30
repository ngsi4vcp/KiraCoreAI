package ru.kiracore.ai.storage.room

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import ru.kiracore.ai.security.AndroidSecureStore

/** Physical Room gateway for the A2 persistence foundation. */
class AndroidRoomPersistenceGateway(
    context: Context,
) : AutoCloseable {
    private val database = KiraRoomDatabase.open(context)
    private val dao = database.dao()
    private val secureStore = AndroidSecureStore(context.applicationContext)

    fun schemaVersion(): Int = KiraRoomDatabase.SCHEMA_VERSION

    fun saveCoreState(payloadJson: String) {
        val json = JSONObject(payloadJson)
        dao.upsertCoreState(
            CoreStateEntity(
                singletonId = 1,
                schemaVersion = json.optInt("schema_version", 1),
                encryptedPayload = seal("core-state", payloadJson),
                updatedAt = json.optString("updated_at", now()),
            ),
        )
    }

    fun loadCoreState(): String? =
        dao.getCoreState()?.let { open("core-state", it.encryptedPayload) }

    fun saveSession(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val sessionId = required(json, "session_id")
        dao.upsertSession(
            SessionEntity(
                sessionId = sessionId,
                createdAt = json.optString("created_at", now()),
                updatedAt = json.optString("updated_at", now()),
                encryptedPayload = seal("session:$sessionId", payloadJson),
            ),
        )
    }

    fun loadSession(sessionId: String): String? =
        dao.getSession(sessionId)?.let { open("session:$sessionId", it.encryptedPayload) }

    fun listSessions(): String =
        JSONArray().also { array ->
            dao.listSessions().forEach { item ->
                array.put(JSONObject(open("session:${item.sessionId}", item.encryptedPayload)))
            }
        }.toString()

    fun saveConversationManifest(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val sessionId = required(json, "session_id")
        dao.upsertConversationManifest(
            ConversationManifestEntity(
                sessionId = sessionId,
                createdAt = json.optString("created_at", now()),
                updatedAt = json.optString("updated_at", now()),
                encryptedPayload = seal("conversation-manifest:$sessionId", payloadJson),
            ),
        )
    }

    fun loadConversationManifest(sessionId: String): String? =
        dao.getConversationManifest(sessionId)?.let {
            open("conversation-manifest:$sessionId", it.encryptedPayload)
        }

    fun listConversationManifests(): String =
        JSONArray().also { array ->
            dao.listConversationManifests().forEach { item ->
                array.put(JSONObject(open("conversation-manifest:${item.sessionId}", item.encryptedPayload)))
            }
        }.toString()

    fun appendConversationMessage(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val messageId = required(json, "id")
        val sessionId = required(json, "session_id")
        dao.upsertConversationMessage(
            ConversationMessageEntity(
                messageId = messageId,
                sessionId = sessionId,
                turn = json.optInt("turn", 0),
                role = required(json, "role"),
                timestamp = json.optString("timestamp", now()),
                encryptedPayload = seal("conversation-message:$messageId", payloadJson),
            ),
        )
    }

    fun recentConversation(sessionId: String, limit: Int): String {
        require(limit >= 0) { "Лимит разговора не может быть отрицательным." }
        if (limit == 0) return "[]"
        val items = dao.recentConversationMessages(sessionId, limit).asReversed()
        return JSONArray().also { array ->
            items.forEach { item ->
                array.put(JSONObject(open("conversation-message:${item.messageId}", item.encryptedPayload)))
            }
        }.toString()
    }

    fun saveMemory(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val memoryId = required(json, "id")
        dao.upsertMemory(
            MemoryRecordEntity(
                memoryId = memoryId,
                status = json.optString("status", "candidate"),
                ownerIdentityId = json.optString("owner_identity_id").takeIf { it.isNotBlank() },
                privacyScope = json.optString("privacy_scope", "Private"),
                updatedAt = json.optString("timestamp", now()),
                encryptedPayload = seal("memory:$memoryId", payloadJson),
            ),
        )
    }

    fun listMemory(): String =
        JSONArray().also { array ->
            dao.listMemory().forEach { item ->
                array.put(JSONObject(open("memory:${item.memoryId}", item.encryptedPayload)))
            }
        }.toString()

    fun listMemoryByStatus(status: String): String =
        JSONArray().also { array ->
            dao.listMemoryByStatus(status).forEach { item ->
                array.put(JSONObject(open("memory:${item.memoryId}", item.encryptedPayload)))
            }
        }.toString()

    fun appendHistory(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val historyId = required(json, "id")
        dao.upsertHistory(
            HistoryEntryEntity(
                historyId = historyId,
                date = json.optString("date", now()),
                encryptedPayload = seal("history:$historyId", payloadJson),
            ),
        )
    }

    fun recentHistory(limit: Int): String {
        require(limit >= 0) { "Лимит истории не может быть отрицательным." }
        if (limit == 0) return "[]"
        val items = dao.recentHistory(limit).asReversed()
        return JSONArray().also { array ->
            items.forEach { item ->
                array.put(JSONObject(open("history:${item.historyId}", item.encryptedPayload)))
            }
        }.toString()
    }

    fun listHistory(): String =
        JSONArray().also { array ->
            dao.listHistory().forEach { item ->
                array.put(JSONObject(open("history:${item.historyId}", item.encryptedPayload)))
            }
        }.toString()

    fun saveOperation(payloadJson: String) {
        val json = JSONObject(payloadJson)
        val operationId = required(json, "operation_id")
        dao.upsertOperation(
            RuntimeOperationEntity(
                operationId = operationId,
                sessionId = required(json, "session_id"),
                phase = required(json, "phase"),
                recoveryState = required(json, "recovery_state"),
                updatedAt = json.optString("updated_at", now()),
                encryptedPayload = seal("operation:$operationId", payloadJson),
            ),
        )
    }

    fun loadOperation(operationId: String): String? =
        dao.getOperation(operationId)?.let { open("operation:$operationId", it.encryptedPayload) }

    fun listOperations(): String =
        JSONArray().also { array ->
            dao.listOperations().forEach { item ->
                array.put(JSONObject(open("operation:${item.operationId}", item.encryptedPayload)))
            }
        }.toString()

    fun deleteConversation(sessionId: String) {
        dao.deleteConversation(sessionId)
    }

    override fun close() {
        database.close()
    }

    private fun seal(aad: String, payload: String): String =
        secureStore.encryptPayload(aad, payload.toByteArray(Charsets.UTF_8))

    private fun open(aad: String, encryptedPayload: String): String =
        secureStore.decryptPayload(aad, encryptedPayload).toString(Charsets.UTF_8)

    private fun required(json: JSONObject, key: String): String =
        json.optString(key).takeIf { it.isNotBlank() }
            ?: error("Отсутствует обязательное поле: $key")

    private fun now(): String = java.time.Instant.now().toString()
}
