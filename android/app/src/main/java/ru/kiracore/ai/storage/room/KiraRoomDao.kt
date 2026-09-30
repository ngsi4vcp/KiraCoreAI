package ru.kiracore.ai.storage.room

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Transaction
import androidx.room.Upsert

@Dao
interface KiraRoomDao {
    @Upsert
    fun upsertCoreState(entity: CoreStateEntity)

    @Query("SELECT * FROM core_state WHERE singletonId = 1")
    fun getCoreState(): CoreStateEntity?

    @Upsert
    fun upsertSession(entity: SessionEntity)

    @Query("SELECT * FROM sessions ORDER BY updatedAt DESC")
    fun listSessions(): List<SessionEntity>

    @Query("SELECT * FROM sessions WHERE sessionId = :sessionId")
    fun getSession(sessionId: String): SessionEntity?

    @Upsert
    fun upsertConversationManifest(entity: ConversationManifestEntity)

    @Query("SELECT * FROM conversation_manifests ORDER BY updatedAt DESC")
    fun listConversationManifests(): List<ConversationManifestEntity>

    @Query("SELECT * FROM conversation_manifests WHERE sessionId = :sessionId")
    fun getConversationManifest(sessionId: String): ConversationManifestEntity?

    @Upsert
    fun upsertConversationMessage(entity: ConversationMessageEntity)

    @Query("SELECT * FROM conversation_messages WHERE sessionId = :sessionId ORDER BY timestamp DESC LIMIT :limit")
    fun recentConversationMessages(sessionId: String, limit: Int): List<ConversationMessageEntity>

    @Upsert
    fun upsertMemory(entity: MemoryRecordEntity)

    @Query("SELECT * FROM memory_records ORDER BY updatedAt DESC")
    fun listMemory(): List<MemoryRecordEntity>

    @Query("SELECT * FROM memory_records WHERE status = :status ORDER BY updatedAt DESC")
    fun listMemoryByStatus(status: String): List<MemoryRecordEntity>

    @Upsert
    fun upsertHistory(entity: HistoryEntryEntity)

    @Query("SELECT * FROM history_entries ORDER BY date DESC LIMIT :limit")
    fun recentHistory(limit: Int): List<HistoryEntryEntity>

    @Upsert
    fun upsertOperation(entity: RuntimeOperationEntity)

    @Query("SELECT * FROM runtime_operations ORDER BY updatedAt DESC")
    fun listOperations(): List<RuntimeOperationEntity>

    @Query("SELECT * FROM runtime_operations WHERE operationId = :operationId")
    fun getOperation(operationId: String): RuntimeOperationEntity?

    @Query("DELETE FROM conversation_messages WHERE sessionId = :sessionId")
    fun deleteConversationMessages(sessionId: String)

    @Query("DELETE FROM conversation_manifests WHERE sessionId = :sessionId")
    fun deleteConversationManifest(sessionId: String)

    @Transaction
    fun deleteConversation(sessionId: String) {
        deleteConversationMessages(sessionId)
        deleteConversationManifest(sessionId)
    }
}
