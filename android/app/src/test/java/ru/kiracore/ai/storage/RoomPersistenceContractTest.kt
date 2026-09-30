package ru.kiracore.ai.storage

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.kiracore.ai.storage.room.KiraRoomDatabase

class RoomPersistenceContractTest {
    @Test
    fun schemaVersionStartsAtOne() {
        assertEquals(1, KiraRoomDatabase.SCHEMA_VERSION)
        assertTrue(KiraRoomDatabase.SCHEMA_VERSION > 0)
    }
}
