# RegisterNatives and exception construction use these exact names/signatures.
-keep class {{PACKAGE_NAME}}.core.sharedcore.NativeBridge { *; }
-keep class {{PACKAGE_NAME}}.core.sharedcore.CoreException { public <init>(int); }
