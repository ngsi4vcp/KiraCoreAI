package ru.kiracore.ai.security

import android.content.Context
import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class AndroidSecureStore(
    context: Context,
) : PlatformSecureStore {
    private val preferences = context.applicationContext.getSharedPreferences(
        PREFS_NAME,
        Context.MODE_PRIVATE,
    )
    private val keyStore: KeyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply {
        load(null)
    }

    override fun put(name: String, value: ByteArray) {
        require(name.isNotBlank()) {
            "Имя записи защищённого хранилища не может быть пустым."
        }
        preferences.edit()
            .putString(name, encryptPayload(name, value))
            .commit()
    }

    override fun get(name: String): ByteArray? {
        val encoded = preferences.getString(name, null) ?: return null
        return decryptPayload(name, encoded)
    }

    fun encryptPayload(aad: String, value: ByteArray): String =
        Base64.encodeToString(encrypt(aad, value), Base64.NO_WRAP)

    fun decryptPayload(aad: String, encoded: String): ByteArray =
        decrypt(aad, Base64.decode(encoded, Base64.NO_WRAP))

    override fun delete(name: String) {
        preferences.edit().remove(name).commit()
    }

    fun isAvailable(): Boolean {
        val key = getOrCreateKey()
        return key.algorithm == AES_ALGORITHM
    }

    private fun encrypt(aad: String, value: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        cipher.updateAAD(aad.toByteArray(StandardCharsets.UTF_8))
        val encrypted = cipher.doFinal(value)
        return ByteArray(cipher.iv.size + encrypted.size).also { packed ->
            System.arraycopy(cipher.iv, 0, packed, 0, cipher.iv.size)
            System.arraycopy(encrypted, 0, packed, cipher.iv.size, encrypted.size)
        }
    }

    private fun decrypt(aad: String, packed: ByteArray): ByteArray {
        require(packed.size > IV_LENGTH_BYTES) {
            "Повреждённая запись защищённого хранилища."
        }
        val iv = packed.copyOfRange(0, IV_LENGTH_BYTES)
        val ciphertext = packed.copyOfRange(IV_LENGTH_BYTES, packed.size)
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(
            Cipher.DECRYPT_MODE,
            getOrCreateKey(),
            GCMParameterSpec(TAG_LENGTH_BITS, iv),
        )
        cipher.updateAAD(aad.toByteArray(StandardCharsets.UTF_8))
        return cipher.doFinal(ciphertext)
    }

    private fun getOrCreateKey(): SecretKey {
        val existing = keyStore.getKey(KEY_ALIAS, null)
        if (existing != null) {
            return existing as SecretKey
        }

        val generator = KeyGenerator.getInstance(AES_ALGORITHM, ANDROID_KEYSTORE)
        generator.init(
            android.security.keystore.KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                android.security.keystore.KeyProperties.PURPOSE_ENCRYPT or
                    android.security.keystore.KeyProperties.PURPOSE_DECRYPT,
            )
                .setBlockModes(android.security.keystore.KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(android.security.keystore.KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(KEY_SIZE_BITS)
                .build(),
        )
        return generator.generateKey()
    }

    companion object {
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val AES_ALGORITHM = "AES"
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
        private const val KEY_ALIAS = "kira.runtime.storage.v1"
        private const val KEY_SIZE_BITS = 256
        private const val TAG_LENGTH_BITS = 128
        private const val IV_LENGTH_BYTES = 12
        private const val PREFS_NAME = "kira_secure_store"
    }
}
