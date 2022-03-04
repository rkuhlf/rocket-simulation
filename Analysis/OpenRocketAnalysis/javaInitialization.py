import jpype

from Helpers.data import load_environment_variable

def jvm_instance():
    # TODO: Understan this, then make it better
    jvm_path = jpype.getDefaultJVMPath()
    jar_path = load_environment_variable("OR_JAR_PATH")

    jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

try:
    jvm_instance()
except OSError as e:
    print(f"JVM is already started, continuing ({e})")