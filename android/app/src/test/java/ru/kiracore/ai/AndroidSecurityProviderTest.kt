package ru.kiracore.ai

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.kiracore.ai.security.AndroidCryptoProvider

class AndroidSecurityProviderTest {
    @Test
    fun cryptoProviderUsesSecureRandomAndSha256() {
        val provider = AndroidCryptoProvider()
        val first = provider.randomBytes(32)
        val second = provider.randomBytes(32)

        assertEqualsLength(first, 32)
        assertEqualsLength(second, 32)
        assertNotEquals(first.toList(), second.toList())
        assertArrayEquals(provider.sha256("test".toByteArray()), provider.sha256("test".toByteArray()))
        assertTrue(provider.sha256("test".toByteArray()).size == 32)
    }

    private fun assertEqualsLength(value: ByteArray, expected: Int) {
        assertTrue("Неверный размер случайного буфера.", value.size == expected)
    }
}
