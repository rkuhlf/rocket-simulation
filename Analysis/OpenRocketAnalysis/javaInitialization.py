import jpype

from Helpers.data import load_environment_variable

# I think I deleted a line from _orhelper to make this work

def initialize_jvm_instance():
    # TODO: Understan this, then make it better
    jvm_path = jpype.getDefaultJVMPath()
    jar_path = load_environment_variable("OR_JAR_PATH")

    try:
        jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")
    except OSError as e:
        print(f"Stopping OSError that JVM is already started, continuing; ({e})")


initialize_jvm_instance()
