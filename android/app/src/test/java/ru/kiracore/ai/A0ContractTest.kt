package ru.kiracore.ai

import org.junit.Assert.assertEquals
import org.junit.Test

class A0ContractTest {
    @Test
    fun applicationIdIsStable() {
        assertEquals("ru.kiracore.ai", BuildConfig.APPLICATION_ID)
    }
}
