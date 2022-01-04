import jpype

def jvm_instance():
    jvm_path = jpype.getDefaultJVMPath()
    jar_path = r"C:\Users\riley\AppData\Local\OpenRocket\app\OpenRocket-15.03.jar"

    jpype.startJVM(jvm_path, "-ea", f"-Djava.class.path={jar_path}")

try:
    jvm_instance()
except OSError as e:
    print(f"JVM is already started, continuing ({e})")