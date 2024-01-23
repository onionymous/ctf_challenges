package com.dicectf2024.dictionaryservice

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInfo
import android.content.pm.PackageManager
import android.content.pm.Signature
import android.util.Base64
import android.util.Log

object IntentChecker {
    private val TAG: String = "IntentChecker"

    private val CALLER_IDENTITY_TAG: String = "__ci"
    private val TIMESTAMP_TAG: String = "__t"
    private val CALLER_IDENTITY_TIMEOUT: Int = 10000

    // signature and package name of DictionaryApp
    private val TRUSTED_PACKAGE_NAME: String = "com.dicectf2024.dictionaryapp"

    // see https://developer.android.com/studio/publish/app-signing
    private val TRUSTED_SIGNATURE_HASH: String =
        "MIICxDCCAawCAQEwDQYJKoZIhvcNAQELBQAwKDETMBEGA1UEAwwKSm9obiBTbWl0aDERMA8GA1UECwwIRGljZUdhbmcwHhcNMjQwMTIyMjE1NzAzWhcNNDkwMTE1MjE1NzAzWjAoMRMwEQYDVQQDDApKb2huIFNtaXRoMREwDwYDVQQLDAhEaWNlR2FuZzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMqJjRJOro8apjIWTLMAReeyYAKkzoblGCamR5TdL4y9xPNfY6RGjeSV4pd3v0-LGwwIj877W-eXdmmq4lImR83HWA8U3SO7QiaHR2E2ahy-cyMJDB0YAYWKICcLP9tm7yLOpTAV6l1w_BmDiOf5zmBTLT1W_41HOfKE8MH4j1WG7zp6la6fLbmGAlZ2JD33PCvaLKEYka7l8DcjMpWvyLkMUVNbjBvV8yrJu7TUgCWnEWGP6g2iEW2K8fYtFaemdAMZHmjGw0iIJLkVjpYziKqgs3-eNgF3o12gjwocjxIIaKy5qOi4x-Gtzl5J9GYusiAtEPTJtxaZCWeog7ABUFsCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEArAog02e-mM140AGj-s1EKK8EDHmHRZcMUTUfW3wVB4Ek-twTE-oaLg8FhrF98_91aDZ7Ab3Nz1CRn5WGDiY6J-_XS9N54AGYmi-fgeG7YXDz9Ju6r_qn4_FzTGeA1cEZBU5wPOW82ICnt5DbS-J11Re32QpvEPTTaMaMyVoFU1So07_fnEleKiIrhh6HvyVQyZwAfgVscN-mpqRCCXGeO12pB340QQ_9IldnlrCY6kebXp8pDPDW9eHcDNlsgt_ZVOM5k8JGqQw8UHLAJxDbRhxKPBqM_lfCqx1sASmuYKL9t-5742L_0yUY2NtLMHiFFir20tKn4foj9VDzcwm9Uw"

    fun isSecure(context: Context, intent: Intent): Boolean {
        // fetch the pending intent created by the caller app
        if (!intent.hasExtra(CALLER_IDENTITY_TAG)) {
            Log.d(TAG, "error - no identity exists")
            return false;
        }
        val pendingIntent: PendingIntent =
            intent.getParcelableExtra(CALLER_IDENTITY_TAG) ?: return false

        // The returned values for package & uid are supplied by the system, so that an application can not spoof them.
        // https://android.googlesource.com/platform/frameworks/base/+/HEAD/core/java/android/app/PendingIntent.java#1129
        // i'm trusting u google
        val callerPackageName: String? = pendingIntent.creatorPackage
        val callerUid: Int = pendingIntent.creatorUid
        Log.d(TAG, "caller: $callerPackageName, $callerUid")
        if (callerPackageName == null || callerPackageName != TRUSTED_PACKAGE_NAME) {
            Log.d(TAG, "error - caller package name mismatch")
            return false
        }

        // check the identity hasn't expired
        val timestamp: Long = intent.getLongExtra(TIMESTAMP_TAG, 0)
        Log.d(TAG, "timestamp: $timestamp")
        if (System.currentTimeMillis() - timestamp > CALLER_IDENTITY_TIMEOUT) {
            Log.d(TAG, "error - identity with timestamp $timestamp has expired")
            return false;
        }

        // query PackageManager for the package that corresponds to the sender
        val packageManager: PackageManager = context.packageManager
        val uid = packageManager.getPackageUid(callerPackageName, PackageManager.GET_SIGNATURES)
        if (uid != callerUid) {
            Log.d(TAG, "error - caller package uid mismatch")
            return false
        }

        val packageInfo: PackageInfo =
            packageManager.getPackageInfo(callerPackageName, PackageManager.GET_SIGNATURES)
        val signatures = packageInfo.signatures
        Log.d(TAG, "signatures: $signatures")
        if (signatures.size != 1) {
            Log.d(TAG, "error - caller package signed with multiple signatures")
            return false
        }
        val signature: Signature = signatures[0]

        // verify that the signature of the installed app with the UID that created the PI
        // is indeed the same as our trusted app
        val signatureHash = Base64.encodeToString(
            signature.toByteArray(),
            Base64.NO_PADDING or Base64.NO_WRAP or Base64.URL_SAFE
        );
        Log.d(TAG, "signatureHash: $signatureHash")

        val isTrusted = TRUSTED_SIGNATURE_HASH == signatureHash
        if (!isTrusted) {
            Log.d(TAG, "error - caller signature mismatch")
        }

        return isTrusted
    }
}