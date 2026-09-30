package ru.kiracore.ai.security

import java.security.MessageDigest
import java.security.SecureRandom

class AndroidCryptoProvider : CryptoProvider {
    private val secureRandom = SecureRandom()

    override fun randomBytes(size: Int): ByteArray {
        require(size > 0) { "Размер случайного буфера должен быть положительным." }
        return ByteArray(size).also(secureRandom::nextBytes)
    }

    override fun sha256(value: ByteArray): ByteArray =
        MessageDigest.getInstance("SHA-256").digest(value)
}
