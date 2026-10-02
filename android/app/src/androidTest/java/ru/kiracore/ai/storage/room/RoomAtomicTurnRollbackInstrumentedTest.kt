package ru.kiracore.ai.storage.room

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class RoomAtomicTurnRollbackInstrumentedTest {
    @Test
    fun physicalRollbackRestoresAllAtomicTurnRecords() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val gateway = AndroidRoomPersistenceGateway(context)

        try {
            val sessionId = "rollback-session"
            val operationId = "rollback-operation"
            val now = "2026-10-02T00:00:00Z"

            gateway.saveCoreState(
                """
                {
                  "schema_version": 1,
                  "runtime_status": "running",
                  "active_session_id": "$sessionId",
                  "turn": 1,
                  "updated_at": "$now"
                }
                """.trimIndent(),
            )
            gateway.saveSession(
                """
                {
                  "session_id": "$sessionId",
                  "created_at": "$now",
                  "updated_at": "$now",
                  "provider": "rollback-test",
                  "model": "baseline"
                }
                """.trimIndent(),
            )
            gateway.saveConversationManifest(
                """
                {
                  "session_id": "$sessionId",
                  "created_at": "$now",
                  "updated_at": "$now",
                  "provider": "rollback-test",
                  "model": "baseline"
                }
                """.trimIndent(),
            )
            gateway.appendConversationMessage(
                """
                {
                  "id": "user-message",
                  "session_id": "$sessionId",
                  "turn": 1,
                  "role": "user",
                  "content": "baseline",
                  "timestamp": "$now"
                }
                """.trimIndent(),
            )
            gateway.appendHistory(
                """
                {
                  "id": "history-baseline",
                  "date": "$now",
                  "event": "baseline",
                  "change": "none",
                  "cause": "test",
                  "consequence": "baseline"
                }
                """.trimIndent(),
            )
            gateway.saveOperation(
                """
                {
                  "operation_id": "$operationId",
                  "session_id": "$sessionId",
                  "phase": "CHECKPOINTED",
                  "checkpoint": "before-model-call",
                  "provider": "rollback-test",
                  "model": "baseline",
                  "recovery_state": "CHECKPOINTED",
                  "updated_at": "$now"
                }
                """.trimIndent(),
            )

            val failingGateway = AndroidRoomPersistenceGateway(
                context,
                atomicCommitFailureInjector = {
                    error("intentional physical rollback failure")
                },
            )

            try {
                failingGateway.commitAtomicTurn(
                    JSONObject()
                        .put(
                            "core_state",
                            JSONObject(
                                """
                                {
                                  "schema_version": 1,
                                  "runtime_status": "waiting",
                                  "active_session_id": "$sessionId",
                                  "turn": 2,
                                  "updated_at": "2026-10-02T00:00:01Z"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .put(
                            "session",
                            JSONObject(
                                """
                                {
                                  "session_id": "$sessionId",
                                  "created_at": "$now",
                                  "updated_at": "2026-10-02T00:00:01Z",
                                  "provider": "rollback-test",
                                  "model": "after-failure"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .put(
                            "conversation_manifest",
                            JSONObject(
                                """
                                {
                                  "session_id": "$sessionId",
                                  "created_at": "$now",
                                  "updated_at": "2026-10-02T00:00:01Z",
                                  "provider": "rollback-test",
                                  "model": "after-failure"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .put(
                            "assistant_message",
                            JSONObject(
                                """
                                {
                                  "id": "assistant-message",
                                  "session_id": "$sessionId",
                                  "turn": 2,
                                  "role": "assistant",
                                  "content": "must rollback",
                                  "timestamp": "2026-10-02T00:00:01Z"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .put(
                            "history",
                            JSONObject(
                                """
                                {
                                  "id": "history-final",
                                  "date": "2026-10-02T00:00:01Z",
                                  "event": "final",
                                  "change": "must rollback",
                                  "cause": "test",
                                  "consequence": "must not persist"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .put(
                            "operation",
                            JSONObject(
                                """
                                {
                                  "operation_id": "$operationId",
                                  "session_id": "$sessionId",
                                  "phase": "COMPLETED",
                                  "checkpoint": "completed",
                                  "provider": "rollback-test",
                                  "model": "after-failure",
                                  "recovery_state": "COMPLETED",
                                  "updated_at": "2026-10-02T00:00:01Z"
                                }
                                """.trimIndent(),
                            ),
                        )
                        .toString(),
                )
                throw AssertionError("Ожидался намеренный отказ внутри Room transaction.")
            } catch (error: IllegalStateException) {
                assertEquals("intentional physical rollback failure", error.message)
            } finally {
                failingGateway.close()
            }

            val core = JSONObject(requireNotNull(gateway.loadCoreState()))
            assertEquals("running", core.getString("runtime_status"))
            assertEquals(1, core.getInt("turn"))

            val session = JSONObject(requireNotNull(gateway.loadSession(sessionId)))
            assertEquals("baseline", session.getString("model"))

            val manifest = JSONObject(
                requireNotNull(gateway.loadConversationManifest(sessionId)),
            )
            assertEquals("baseline", manifest.getString("model"))

            val messages = org.json.JSONArray(gateway.recentConversation(sessionId, 10))
            assertEquals(1, messages.length())
            assertEquals("user-message", messages.getJSONObject(0).getString("id"))

            val history = org.json.JSONArray(gateway.listHistory())
            assertEquals(1, history.length())
            assertEquals(
                "history-baseline",
                history.getJSONObject(0).getString("id"),
            )

            val operations = org.json.JSONArray(gateway.listOperations())
            assertEquals(1, operations.length())
            assertNotNull(operations.getJSONObject(0))
            assertEquals("CHECKPOINTED", operations.getJSONObject(0).getString("phase"))
        } finally {
            gateway.close()
            context.deleteDatabase("kira-core.db")
        }
    }
}
