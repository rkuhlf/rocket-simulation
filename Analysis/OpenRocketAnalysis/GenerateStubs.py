# Creates autocompletion for openrocket
# I have hidden the stubs file that is generated in my .vscode settings
# 

import jpype
import stubgenj

# from java import io
# io.

jvm_path = r"C:\Program Files\Java\jdk1.8.0_301\jre\bin\server\jvm.dll"
jar_path = r"C:\Users\riley\AppData\Local\OpenRocket\app\OpenRocket-15.03.jar"

jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

import jpype.imports
# import java.util  # type: ignore
# import java.io.File 

# from net.sf.openrocket import simulation # type: ignore

# jpype.JPackage("net").sf.openrocket
stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)
# stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)



"""
#%% Sample given by website

import jpype
import stubgenj

jpype.startJVM(None, convertStrings=True)  # noqa
import jpype.imports  # noqa
import java.util  # noqa

stubgenj.generateJavaStubs([java.util], useStubsSuffix=True)
"""