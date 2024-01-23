# spellbound (dicectf2024)

misc, android, easy

* you'll probably need [Android Studio](https://developer.android.com/studio)
* all the apps are tested on Pixel 3a AVD API 34

## files

`chal.zip` has the files that should be distributed in the challenge download:
* DictionaryApp.apk (signed app) - same as remote
* DictionaryService.apk (can be signed or unsigned, doesn't really matter) - modified APK to include fake flag. remote will have real flag

There's no obfuscation, we expect people to just go decompile the apks.

The key used to sign the app to create the hardcoded signature in the apps' identity check is included in the repo.
The key alias is `dictionary-app-release` and the passcode is `pepegaman`, and the keystore password is also `pepegaman`.
Since this key is pretty related to the challenge the keystore is included in this repo for reproducibility reasons,
but it goes without saying don't use this keystore for anything important etc.

## description

This challenge required exploiting a behavior of [Android bound services](https://developer.android.com/develop/background-work/services/bound-services). Namely this part:
> You can connect multiple clients to a service simultaneously. However, the system caches the IBinder service communication channel. In other words, the system calls the service's onBind() method to generate the IBinder only when the first client binds. The system then delivers that same IBinder to all additional clients that bind to that same service, without calling onBind() again.

### DictionaryService
This app only exports a single service, DictionaryService, which serves a bunch of words and their definitions, including the flag. Even though the service is exported, this service is only intended to be bound to from DictionaryApp. To ensure this, it has a permission check in `onBind` that is pretty restrictive - it checks that the incoming intent to bind to the service is trusted. "trusted" means having a serialized extra that is a PendingIntent. A PendingIntent is used since the creator package name and UID is set by the system and cannot be spoofed (see [PendingIntent.java](https://android.googlesource.com/platform/frameworks/base/+/HEAD/core/java/android/app/PendingIntent.java)). (we're just taking this for granted from Google. If it turns out there's some unforseen bug and this isn't true, well fuck). It also has DictionaryApp's signature hardcoded so after it receives the intent, it'll query PackageManager for the package corresponding to the package name, and get the signature, and will check that it matches. If not, it'll just return `null` as the binder interface and not the actual binder.

### DictionaryApp
This app has an exported activity that other apps can launch. The activity will bind to DictionaryService in `onCreate` and then send words to it / receives definitions back, and this gets rendered onscreen.

## solution

The solution is to write an attacker app that
1. Launches DictionaryApp, triggering it to bind to DictionaryService
2. Tries to bind to DictionaryService after DictionaryApp has successfully binded. Since `onBind` is only ever called once and the same interface is returned to all clients, this bypasses the permission check. Now you can call `getData` on the service with the word `flag` to get flag, and print it out in logcat (which the solve service will give you)

The easiest is just to sleep for a few seconds after launching DictionaryApp's DefinitionActivity and then try to call `bindService`. Or you can start another service that binds to DictionaryService.

Note that if an untrusted app tries to bind to DictionaryService with an intent without the proper identity, DictionaryService will just return `null`. The result of `bindService` will still show as `true` but you can't do anything with this interface.