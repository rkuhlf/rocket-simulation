# Creates autocompletion for openrocket
# I have hidden the stubs file that is generated in my .vscode settings

import jpype
import stubgenj

from Helpers.data import load_environment_variable

jvm_path = load_environment_variable("JVM_PATH")
jar_path = load_environment_variable("OR_JAR_PATH")


jpype.startJVM(jvm_path, "-ea", classpath=[jar_path])
import jpype.imports  # noqa

stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)


# \U is the Unicode Escape character