

import orhelper

def new_or_instance():
    return orhelper.OpenRocketInstance(jar_path=r"C:\Users\riley\AppData\Local\OpenRocket\app\OpenRocket-15.03.jar")

def most_updated_sim(orhelper):
    doc = orhelper.load_doc(r"C:\Users\riley\Downloads\CorrectedMasses (1).ork")
    sim = getSimulationByName(doc, 'White Sands Average')

    return sim

def getSimulationNames(document):
    print([sim.getName() for sim in document.getSimulations()])

def getSimulationByName(document, name):
    """Accepts openrocket document; returns simulation with the given name"""

    for sim in document.getSimulations():
        if sim.getName() == name:
            return sim

    return None

def apogee(sim):
    return sim.getSimulatedData().getMaxAltitude()

