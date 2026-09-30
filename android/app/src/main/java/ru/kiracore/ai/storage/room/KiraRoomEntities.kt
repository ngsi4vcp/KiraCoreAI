package ru.kiracore.ai.storage.room

import androidx.room.Entity
import androidx.room.Index

@Entity(tableName = "core_state")
data class CoreStateEntity(
    @androidx.room.PrimaryKey val singletonId: Int = 1,
    val schemaVersion: Int,
    val encryptedPayload: String,
    val updatedAt: String,
)

@Entity(tableName = "sessions", indices = [Index("updatedAt")])
data class SessionEntity(
    @androidx.room.PrimaryKey val sessionId: String,
    val createdAt: String,
    val updatedAt: String,
    val encryptedPayload: String,
)

@Entity(
    tableName = "conversation_manifests",
    indices = [Index("updatedAt")],
)
data class ConversationManifestEntity(
    @androidx.room.PrimaryKey val sessionId: String,
    val createdAt: String,
    val updatedAt: String,
    val encryptedPayload: String,
)

@Entity(
    tableName = "conversation_messages",
    indices = [Index(value = ["sessionId", "timestamp"])],
)
data class ConversationMessageEntity(
    @androidx.room.PrimaryKey val messageId: String,
    val sessionId: String,
    val turn: Int,
    val role: String,
    val timestamp: String,
    val encryptedPayload: String,
)

@Entity(
    tableName = "memory_records",
    indices = [Index("status"), Index("ownerIdentityId"), Index("privacyScope")],
)
data class MemoryRecordEntity(
    @androidx.room.PrimaryKey val memoryId: String,
    val status: String,
    val ownerIdentityId: String?,
    val privacyScope: String,
    val updatedAt: String,
    val encryptedPayload: String,
)

@Entity(
    tableName = "history_entries",
    indices = [Index("date")],
)
data class HistoryEntryEntity(
    @androidx.room.PrimaryKey val historyId: String,
    val date: String,
    val encryptedPayload: String,
)

@Entity(
    tableName = "runtime_operations",
    indices = [Index("sessionId"), Index("updatedAt")],
)
data class RuntimeOperationEntity(
    @androidx.room.PrimaryKey val operationId: String,
    val sessionId: String,
    val phase: String,
    val recoveryState: String,
    val updatedAt: String,
    val encryptedPayload: String,
)
