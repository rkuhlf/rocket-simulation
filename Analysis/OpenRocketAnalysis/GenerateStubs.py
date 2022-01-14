
# OG
# Creates autocompletion for openrocket
# I have hidden the stubs file that is generated in my .vscode settings
# 

import jpype
import stubgenj


jvm_path = r"C:\Program Files\Java\jdk1.8.0_251\jre\bin\server\jvm.dll"
jar_path = r"C:\Users\riley\AppData\Local\OpenRocket\app\OpenRocket-15.03.jar"

jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

import jpype.imports # any java imports have to come after this imports import
from java import io

# import java.util  # type: ignore
import java.io.File # type: ignore

# from net.sf.openrocket import simulation # type: ignore

# jpype.JPackage("net").sf.openrocket
stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)









# # Creates autocompletion for openrocket
# # I have hidden the stubs file that is generated in my .vscode settings
# # 

# import jpype
# import stubgenj

from Helpers.data import load_environment_variable

# # from java import io
# # io.
jvm_path = load_environment_variable("JVM_PATH")
jar_path = load_environment_variable("OR_JAR_PATH")

# jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

# import jpype.imports
# # import java.util  # type: ignore
# # import java.io.File 

# # from net.sf.openrocket import simulation # type: ignore

# # jpype.JPackage("net").sf.openrocket
# stubgenj.generateJavaStubs([jpype.JPackage("net.sf.openrocket")], useStubsSuffix=True)
# # stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)




#%% Sample given by website

import jpype
import stubgenj

# cpopt="-Djava.class.path=%s" % ("/Users/me/jpypeTest")
# Very possible that I am not using the correct path here. I think that perhaps I want the 
jpype.startJVM(jvm_path, "-ea", r"-Djava.class.path=C:\Users\rkuhlman813\Downloads\openrocket-unstable\openrocket-unstable\core\src\net\sf\openrocket")
import jpype.imports  # noqa
# from jpype.JPackage("net").sf.openrocket import simulation  # noqa
# maybe also try a classpath argument with a list of paths: classpath=['lib/*', 'classes']

stubgenj.generateJavaStubs([jpype.JPackage("net").sf.openrocket], useStubsSuffix=True)

# \U is the Unicode Escape character

# Maybe it is supposed to be a JClass with the local installation of the openrocket source
# C:\Users\rkuhlman813\Downloads\openrocket-unstable\openrocket-unstable\core\src\net\sf\openrocket\aerodynamics\Warning.java

# I think that if you put the openrocket stuff in the same folder as the python script, you can use the jpype.imports functionality to allow you to import it