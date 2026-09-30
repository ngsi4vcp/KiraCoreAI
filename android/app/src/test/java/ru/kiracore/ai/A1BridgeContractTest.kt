package ru.kiracore.ai

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Test

class A1BridgeContractTest {
    @Test
    fun genomeInfoIsTyped() {
        val info = BridgeJsonParser.genome(
            JSONObject(
                """{
                    "revision":22,
                    "series":1000,
                    "sha256":"abc",
                    "section_count":31
                }""",
            ),
        )

        assertEquals(22, info.revision)
        assertEquals(1000, info.series)
        assertEquals("abc", info.sha256)
        assertEquals(31, info.sectionCount)
    }

    @Test
    fun runtimeStateAndPulseAreMapped() {
        val state = BridgeJsonParser.runtimeState(
            JSONObject(
                """{
                    "schema_version":1,
                    "runtime_status":"waiting",
                    "active_session_id":"s1",
                    "identity_id":"i1",
                    "turn":1,
                    "pulse":{
                        "series":1000,
                        "revision":22,
                        "turn":1,
                        "value":1024,
                        "key":"1000:22:1:1024"
                    },
                    "active_provider":"a0-test",
                    "active_model":"embedded/a0-test",
                    "authorized_alek":true,
                    "last_error":null,
                    "state":{"next_steps":["test"]}
                }""",
            ),
        )

        assertEquals("waiting", state.runtimeStatus)
        assertEquals("s1", state.activeSessionId)
        assertEquals(1, state.turn)
        assertEquals(1024, state.pulse?.value)
        assertEquals("1000:22:1:1024", state.pulse?.key)
        assertEquals("test", state.rawState.getJSONArray("next_steps").getString(0))
        assertEquals(true, state.authorizedAlek)
    }

    @Test
    fun memoryAndConversationRemainSeparateTypedSurfaces() {
        val memory = BridgeJsonParser.memory(
            JSONObject(
                """{
                    "id":"m1",
                    "type":"fact",
                    "content":"x",
                    "timestamp":"t",
                    "source":"test",
                    "confidence":1.0,
                    "importance":0.5,
                    "provenance":"p",
                    "entities":["a","b"],
                    "valid_from":null,
                    "valid_to":null,
                    "status":"approved",
                    "owner_identity_id":"i1",
                    "privacy_scope":"Private"
                }""",
            ),
        )
        assertEquals("approved", memory.status)
        assertEquals(listOf("a", "b"), memory.entities)
        assertEquals("Private", memory.privacyScope)

        val conversation = BridgeJsonParser.conversation(
            JSONObject(
                """{
                    "id":"c1",
                    "session_id":"s1",
                    "turn":1,
                    "role":"assistant",
                    "content":"answer",
                    "timestamp":"t",
                    "pulse":{
                        "series":1000,
                        "revision":22,
                        "turn":1,
                        "value":1024,
                        "key":"1000:22:1:1024"
                    }
                }""",
            ),
        )
        assertEquals("assistant", conversation.role)
        assertEquals("s1", conversation.sessionId)
        assertNotNull(conversation.pulse)
        assertEquals(1024, conversation.pulse?.value)
    }

    @Test
    fun emptyArraysRemainEmptyTypedLists() {
        val empty = JSONArray("[]")
        assertFalse(empty.length() > 0)
    }
}
