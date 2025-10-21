package no.nnsctf.grooves

import java.io.FilePermission
import java.security.Permission

class JailSecurityManager : SecurityManager() {
    override fun checkPermission(perm: Permission?) {
        if (perm is FilePermission && "flag" in perm.name) {
            throw SecurityException("Naughty!")
        }
        if (perm is RuntimePermission && perm.name == "setSecurityManager") {
            throw SecurityException("Naughty!")
        }
    }
}