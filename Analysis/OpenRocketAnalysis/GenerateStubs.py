# Creates autocompletion for openrocket
# I have hidden the stubs file that is generated in my .vscode settings
# 

import jpype
import stubgenj

from java import io # type: ignore
# io.

jvm_path = r"C:\Program Files\Java\jdk1.8.0_251\jre\bin\server\jvm.dll"
jar_path = r"C:\Users\riley\AppData\Local\OpenRocket\app\OpenRocket-15.03.jar"

jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

import jpype.imports
# import java.util  # type: ignore
import java.io.File # type: ignore

# from net.sf.openrocket import simulation # type: ignore

# jpype.JPackage("net").sf.openrocket
stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)

