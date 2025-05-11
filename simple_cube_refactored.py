# Imports: all required Abaqus modules
from abaqus import *
from abaqusConstants import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

class SimpleCubeModel:
    def __init__(self, model_name='Model-1', part_name='Cube', job_name='SimpleCube'):
        # Initialize model, part, and job names
        self.model_name = model_name
        self.part_name = part_name
        self.job_name = job_name
        self.model = mdb.Model(name=self.model_name)

    def create_geometry(self, size=10.0):
        # Create a cube by sketching a square and extruding it into 3D
        sketch = self.model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
        sketch.rectangle(point1=(0.0, 0.0), point2=(size, size))
        part = self.model.Part(name=self.part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        part.BaseSolidExtrude(depth=size, sketch=sketch)
        del self.model.sketches['__profile__']  # Clean up sketch after use

    def define_material(self, youngs_modulus=1000.0, poisson_ratio=0.3):
        # Define material properties and assign section to the cube
        material = self.model.Material(name='myMaterial')
        material.Elastic(table=((youngs_modulus, poisson_ratio),))
        self.model.HomogeneousSolidSection(name='Homogeneous', material='myMaterial')

        part = self.model.parts[self.part_name]
        part.Set(name='Whole Part', cells=part.cells[:])
        part.SectionAssignment(region=part.sets['Whole Part'], sectionName='Homogeneous',
                               offset=0.0, offsetType=MIDDLE_SURFACE,
                               offsetField='', thicknessAssignment=FROM_SECTION)

    def mesh_part(self, size=2.0):
        # Set global seed size and mesh the part
        part = self.model.parts[self.part_name]
        part.seedPart(size=size, deviationFactor=0.1, minSizeFactor=0.1)
        part.generateMesh()

    def create_assembly(self):
        # Place part in the assembly as a dependent instance
        assembly = self.model.rootAssembly
        assembly.DatumCsysByDefault(CARTESIAN)
        part = self.model.parts[self.part_name]
        assembly.Instance(name=f'{self.part_name}-1', part=part, dependent=ON)

    def apply_boundary_conditions(self):
        # Apply boundary conditions and step
        self.model.StaticStep(name='Loading', previous='Initial')
        instance = self.model.rootAssembly.instances[f'{self.part_name}-1']
        back_face = instance.faces.findAt(((0.0, 3.333333, 6.666667),))
        self.model.rootAssembly.Set(name='BackFace', faces=back_face)

        self.model.DisplacementBC(name='Fixed', createStepName='Initial',
                                  region=self.model.rootAssembly.sets['BackFace'],
                                  u1=SET, u2=SET, u3=SET,
                                  ur1=SET, ur2=SET, ur3=SET)

    def apply_load(self):
        # Apply a point load at the far top corner node
        instance = self.model.rootAssembly.instances[f'{self.part_name}-1']
        load_vertex = instance.vertices.findAt(((10.0, 10.0, 10.0),))
        self.model.rootAssembly.Set(name='LoadNode', vertices=load_vertex)

        self.model.ConcentratedForce(name='PointLoad', createStepName='Loading',
                                     region=self.model.rootAssembly.sets['LoadNode'],
                                     cf2=-3.0)  # Force in Y-direction

    def create_and_submit_job(self):
        # Define, submit, and wait for job completion
        job = mdb.Job(name=self.job_name, model=self.model_name,
                      description='Simple Cube Test',
                      type=ANALYSIS, memory=90, memoryUnits=PERCENTAGE,
                      explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE,
                      getMemoryFromAnalysis=True, resultsFormat=ODB)

        job.submit(consistencyChecking=OFF)
        job.waitForCompletion()

def main():
    # Instantiate and run a simple cube simulation
    cube = SimpleCubeModel()
    cube.create_geometry(size=10.0)
    cube.define_material(youngs_modulus=1000.0, poisson_ratio=0.3)
    cube.mesh_part(size=2.0)
    cube.create_assembly()
    cube.apply_boundary_conditions()
    cube.apply_load()
    cube.create_and_submit_job()

if __name__ == '__main__':
    main()
