# Import necessary Abaqus modules
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

# ---------------------------------------
# Create cube geometry
# ---------------------------------------

# Create a new 2D sketch for the cube's base (a 10x10 square)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
    point2=(10.0, 10.0))

# Create a 3D deformable solid part by extruding the square to a depth of 10
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Cube', type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Cube'].BaseSolidExtrude(depth=10.0, sketch=
    mdb.models['Model-1'].sketches['__profile__'])

# Remove the sketch from memory once extrusion is complete
del mdb.models['Model-1'].sketches['__profile__']

# ---------------------------------------
# Define material and assign section
# ---------------------------------------

# Define a linear elastic material with E = 1000, ν = 0.3
mdb.models['Model-1'].Material(name='myMaterial')
mdb.models['Model-1'].materials['myMaterial'].Elastic(table=((1000.0, 0.3), ))

# Create a homogeneous solid section using the material
mdb.models['Model-1'].HomogeneousSolidSection(material='myMaterial', name='Homogeneous', thickness=None)

# Create a set containing all cells in the part (i.e., the full volume)
mdb.models['Model-1'].parts['Cube'].Set(cells=
    mdb.models['Model-1'].parts['Cube'].cells.getSequenceFromMask(('[#1 ]', ), ), 
    name='Whole Part')

# Assign the material section to the entire cube
mdb.models['Model-1'].parts['Cube'].SectionAssignment(offset=0.0, 
    offsetField='', offsetType=MIDDLE_SURFACE, 
    region=mdb.models['Model-1'].parts['Cube'].sets['Whole Part'], 
    sectionName='Homogeneous', thicknessAssignment=FROM_SECTION)

# ---------------------------------------
# Mesh the part
# ---------------------------------------

# Define the global mesh seed size and mesh parameters
mdb.models['Model-1'].parts['Cube'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=2.0)

# Generate the mesh
mdb.models['Model-1'].parts['Cube'].generateMesh()

# ---------------------------------------
# Create assembly instance
# ---------------------------------------

# Define the global coordinate system
mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)

# Add the cube part as an instance in the assembly
mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Cube-1', 
    part=mdb.models['Model-1'].parts['Cube'])

# ---------------------------------------
# Apply boundary conditions and loads
# ---------------------------------------

# Create a static step named 'Loading' after the initial step
mdb.models['Model-1'].StaticStep(name='Loading', previous='Initial')

# Create a set for the "back face" (x=0) to fix in all DOFs
mdb.models['Model-1'].rootAssembly.Set(faces=
    mdb.models['Model-1'].rootAssembly.instances['Cube-1'].faces.findAt(((
    0.0, 3.333333, 6.666667), )), name='BackFace')

# Apply a fixed boundary condition (all displacements and rotations set to 0) on the back face
mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Initial', 
    distributionType=UNIFORM, fieldName='', localCsys=None, name='Fixed', 
    region=mdb.models['Model-1'].rootAssembly.sets['BackFace'], 
    u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)

# Define a node at the top far corner of the cube to apply the load
mdb.models['Model-1'].rootAssembly.Set(name='LoadNode', vertices=
    mdb.models['Model-1'].rootAssembly.instances['Cube-1'].vertices.findAt(((
    10.0, 10.0, 10.0), )))

# Apply a concentrated force of -3.0 in the Y direction (cf2) to the corner node
mdb.models['Model-1'].ConcentratedForce(cf2=-3.0, createStepName='Loading', 
    distributionType=UNIFORM, field='', localCsys=None, name='PointLoad', 
    region=mdb.models['Model-1'].rootAssembly.sets['LoadNode'])

# ---------------------------------------
# Submit job
# ---------------------------------------

# Create a job to run the simulation
mdb.Job(name='SimpleCube', model='Model-1', type=ANALYSIS, memory=90, 
    memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, 
    description='', getMemoryFromAnalysis=True, echoPrint=OFF, modelPrint=OFF, 
    contactPrint=OFF, historyPrint=OFF, resultsFormat=ODB, scratch='',
    userSubroutine='', waitHours=0, waitMinutes=0, queue=None, atTime=None)

# Submit the job without consistency checking
mdb.jobs['SimpleCube'].submit(consistencyChecking=OFF)
