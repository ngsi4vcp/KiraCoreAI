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
        val cipher = newCipher(Cipher.ENCRYPT_MODE, name)
        val encrypted = cipher.doFinal(value)
        val packed = ByteArray(cipher.iv.size + encrypted.size)
        System.arraycopy(cipher.iv, 0, packed, 0, cipher.iv.size)
        System.arraycopy(encrypted, 0, packed, cipher.iv.size, encrypted.size)
        preferences.edit()
            .putString(name, Base64.encodeToString(packed, Base64.NO_WRAP))
            .commit()
    }

    override fun get(name: String): ByteArray? {
        val encoded = preferences.getString(name, null) ?: return null
        val packed = Base64.decode(encoded, Base64.NO_WRAP)
        require(packed.size > IV_LENGTH_BYTES) {
            "Повреждённая запись защищённого хранилища."
        }
        val iv = packed.copyOfRange(0, IV_LENGTH_BYTES)
        val ciphertext = packed.copyOfRange(IV_LENGTH_BYTES, packed.size)
        val cipher = newCipher(Cipher.DECRYPT_MODE, name, iv)
        return cipher.doFinal(ciphertext)
    }

    override fun delete(name: String) {
        preferences.edit().remove(name).commit()
    }

    fun isAvailable(): Boolean {
        val key = getOrCreateKey()
        return key.algorithm == AES_ALGORITHM
    }

    private fun newCipher(
        mode: Int,
        name: String,
        iv: ByteArray? = null,
    ): Cipher {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        if (mode == Cipher.ENCRYPT_MODE) {
            cipher.init(mode, getOrCreateKey())
        } else {
            cipher.init(
                mode,
                getOrCreateKey(),
                GCMParameterSpec(TAG_LENGTH_BITS, iv ?: error("IV обязателен.")),
            )
        }
        cipher.updateAAD(name.toByteArray(StandardCharsets.UTF_8))
        return cipher
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
