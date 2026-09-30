package ru.kiracore.ai.storage.room

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        CoreStateEntity::class,
        SessionEntity::class,
        ConversationManifestEntity::class,
        ConversationMessageEntity::class,
        MemoryRecordEntity::class,
        HistoryEntryEntity::class,
        RuntimeOperationEntity::class,
    ],
    version = 1,
    exportSchema = true,
)
abstract class KiraRoomDatabase : RoomDatabase() {
    abstract fun dao(): KiraRoomDao

    companion object {
        const val SCHEMA_VERSION = 1
        private const val DATABASE_NAME = "kira-core.db"

        fun open(context: Context): KiraRoomDatabase =
            Room.databaseBuilder(
                context.applicationContext,
                KiraRoomDatabase::class.java,
                DATABASE_NAME,
            ).build()
    }
}
